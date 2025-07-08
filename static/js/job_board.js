// Job Board JavaScript functionality
let jobCounter = 1;

document.addEventListener('DOMContentLoaded', function() {
    initializeJobBoard();
});

function initializeJobBoard() {
    const addJobBtn = document.getElementById('add-job-btn');
    addJobBtn.addEventListener('click', createBlankJobCard);
    
    // Initialize drag and drop
    initializeDragAndDrop();
}

function createBlankJobCard() {
    const jobId = `JOB-${String(jobCounter).padStart(3, '0')}`;
    
    // Create ticket in database
    fetch('/api/tickets', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            job_id: jobId,
            customer_name: null,
            service_type: null,
            status: 'pending',
            priority: 'medium',
            description: 'New septic service job'
        })
    })
    .then(response => response.json())
    .then(ticket => {
        // Create the visual card
        const pendingContainer = document.querySelector('[data-status="pending"]');
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        jobCard.draggable = true;
        jobCard.dataset.jobId = ticket.job_id;
        jobCard.dataset.ticketId = ticket.id;
        
        jobCard.innerHTML = `
            <h4>New Septic Job</h4>
            <p class="job-id">Job ID: ${ticket.job_id}</p>
            <p>Customer: [Not assigned]</p>
            <p>Service: [Not specified]</p>
            <span class="job-status status-pending">Pending</span>
        `;
        
        pendingContainer.appendChild(jobCard);
        jobCounter++;
        
        // Add drag event listeners to the new card
        addDragEventListeners(jobCard);
    })
    .catch(error => {
        console.error('Error creating ticket:', error);
        alert('Failed to create ticket. Please try again.');
    });
}

function initializeDragAndDrop() {
    const containers = document.querySelectorAll('.card-container');
    
    containers.forEach(container => {
        container.addEventListener('dragover', handleDragOver);
        container.addEventListener('drop', handleDrop);
        container.addEventListener('dragenter', handleDragEnter);
        container.addEventListener('dragleave', handleDragLeave);
    });
}

function addDragEventListeners(card) {
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
}

function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.jobId);
    e.target.classList.add('dragging');
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
}

function handleDragEnter(e) {
    e.preventDefault();
    e.target.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.target.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.target.classList.remove('drag-over');
    
    const jobId = e.dataTransfer.getData('text/plain');
    const draggedCard = document.querySelector(`[data-job-id="${jobId}"]`);
    const targetContainer = e.target.closest('.card-container');
    
    if (draggedCard && targetContainer) {
        targetContainer.appendChild(draggedCard);
        updateJobStatus(draggedCard, targetContainer.dataset.status);
    }
}

function updateJobStatus(card, newStatus) {
    const statusElement = card.querySelector('.job-status');
    statusElement.className = `job-status status-${newStatus}`;
    statusElement.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1).replace('-', ' ');
    
    // Update status in database
    const ticketId = card.dataset.ticketId;
    if (ticketId) {
        fetch(`/api/tickets/${ticketId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: newStatus
            })
        })
        .then(response => response.json())
        .then(ticket => {
            console.log('Ticket status updated:', ticket);
        })
        .catch(error => {
            console.error('Error updating ticket status:', error);
        });
    }
}
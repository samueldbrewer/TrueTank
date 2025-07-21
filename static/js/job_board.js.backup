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
    
    // Load existing tickets
    loadExistingTickets();
}

function loadExistingTickets() {
    fetch('/api/tickets')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(tickets => {
            // Group tickets by status and sort by column_position
            const ticketsByStatus = {
                'pending': [],
                'in-progress': [],
                'completed': []
            };
            
            tickets.forEach(ticket => {
                if (ticketsByStatus[ticket.status]) {
                    ticketsByStatus[ticket.status].push(ticket);
                }
            });
            
            // Sort each group by column_position and create cards in order
            Object.keys(ticketsByStatus).forEach(status => {
                ticketsByStatus[status]
                    .sort((a, b) => (a.column_position || 0) - (b.column_position || 0))
                    .forEach(ticket => {
                        createJobCardFromTicket(ticket);
                    });
            });
            
            // Update job counter to avoid ID conflicts
            // Find highest job number and increment
            let maxJobNum = 0;
            tickets.forEach(ticket => {
                const match = ticket.job_id.match(/JOB-(\d+)/);
                if (match) {
                    maxJobNum = Math.max(maxJobNum, parseInt(match[1]));
                }
            });
            jobCounter = maxJobNum + 1;
        })
        .catch(error => {
            console.error('Error loading tickets:', error);
            // Set default job counter if API fails
            jobCounter = 1;
        });
}

function createJobCardFromTicket(ticket) {
    const container = document.querySelector(`[data-status="${ticket.status}"]`);
    if (!container) return;
    
    const jobCard = document.createElement('div');
    jobCard.className = 'job-card';
    jobCard.draggable = true;
    jobCard.dataset.jobId = ticket.job_id;
    jobCard.dataset.ticketId = ticket.id;
    
    // Calculate time info
    const scheduledDate = ticket.scheduled_date ? new Date(ticket.scheduled_date).toLocaleDateString() : 'Not scheduled';
    const estimatedCost = ticket.estimated_cost ? `$${ticket.estimated_cost.toFixed(2)}` : 'TBD';
    const duration = ticket.estimated_duration ? `${ticket.estimated_duration} min` : 'TBD';
    
    jobCard.innerHTML = `
        <div class="card-header">
            <h4>${ticket.service_type || 'Septic Service'}</h4>
            <span class="job-id">${ticket.job_id}</span>
        </div>
        <div class="card-body">
            <div class="customer-info">
                <strong>${ticket.customer_name || '[Not assigned]'}</strong>
                ${ticket.customer_phone ? `<br><small>${ticket.customer_phone}</small>` : ''}
            </div>
            <div class="service-details">
                <div class="detail-item">
                    <span class="label">Scheduled:</span>
                    <span class="value">${scheduledDate}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Technician:</span>
                    <span class="value">${ticket.assigned_technician || 'Unassigned'}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Cost:</span>
                    <span class="value">${estimatedCost}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Duration:</span>
                    <span class="value">${duration}</span>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <span class="job-status status-${ticket.status}">${ticket.status.charAt(0).toUpperCase() + ticket.status.slice(1).replace('-', ' ')}</span>
            <span class="priority-badge priority-${ticket.priority}">${ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}</span>
        </div>
        <div class="card-actions">
            <button class="btn-icon" onclick="viewTicketDetails(${ticket.id})" title="View Details">
                <i class="icon-eye">👁️</i>
            </button>
            <button class="btn-icon" onclick="editTicket(${ticket.id})" title="Edit">
                <i class="icon-edit">✏️</i>
            </button>
            <button class="btn-icon btn-delete" onclick="deleteTicket(${ticket.id}, '${ticket.job_id}')" title="Delete">
                <i class="icon-delete">🗑️</i>
            </button>
        </div>
    `;
    
    container.appendChild(jobCard);
    
    // Add drag event listeners to the card
    addDragEventListeners(jobCard);
}

function viewTicketDetails(ticketId) {
    window.location.href = `/ticket/${ticketId}`;
}

function editTicket(ticketId) {
    window.location.href = `/ticket/${ticketId}/edit`;
}

function deleteTicket(ticketId, jobId) {
    if (confirm(`Are you sure you want to delete ticket "${jobId}"? This action cannot be undone.`)) {
        fetch(`/api/tickets/${ticketId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                // Remove the card from the DOM
                const card = document.querySelector(`[data-ticket-id="${ticketId}"]`);
                if (card) {
                    card.remove();
                }
                alert('Ticket deleted successfully!');
            } else {
                alert('Error deleting ticket: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to delete ticket. Please try again.');
        });
    }
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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(ticket => {
        // Create the visual card using the same function
        createJobCardFromTicket(ticket);
        jobCounter++;
    })
    .catch(error => {
        console.error('Error creating ticket:', error);
        alert('Failed to create ticket. Please try again. Error: ' + error.message);
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
        // Calculate the new position based on drop location
        const newPosition = calculateDropPosition(e, targetContainer);
        const newStatus = targetContainer.dataset.status;
        
        // Insert the card at the correct position
        insertCardAtPosition(draggedCard, targetContainer, newPosition);
        
        // Update the database with new position and status
        updateTicketPosition(draggedCard, newStatus, newPosition);
    }
}

function updateTicketPosition(card, newStatus, newPosition) {
    const statusElement = card.querySelector('.job-status');
    statusElement.className = `job-status status-${newStatus}`;
    statusElement.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1).replace('-', ' ');
    
    // Update position and status in database using reorder endpoint
    const ticketId = card.dataset.ticketId;
    if (ticketId) {
        fetch('/api/tickets/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticket_id: parseInt(ticketId),
                new_status: newStatus,
                new_position: newPosition
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                console.log('Ticket position updated:', result.ticket);
            } else {
                console.error('Error updating ticket position:', result.error);
                alert('Failed to update ticket position: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error updating ticket position:', error);
            alert('Failed to update ticket position. Please refresh and try again.');
        });
    }
}

function calculateDropPosition(event, targetContainer) {
    const cards = Array.from(targetContainer.children);
    let newPosition = cards.length; // Default to end
    
    for (let i = 0; i < cards.length; i++) {
        const card = cards[i];
        const rect = card.getBoundingClientRect();
        const cardMiddle = rect.top + rect.height / 2;
        
        if (event.clientY < cardMiddle) {
            newPosition = i;
            break;
        }
    }
    
    return newPosition;
}

function insertCardAtPosition(card, container, position) {
    const cards = Array.from(container.children);
    
    if (position >= cards.length) {
        // Insert at the end
        container.appendChild(card);
    } else {
        // Insert before the card at the target position
        container.insertBefore(card, cards[position]);
    }
}
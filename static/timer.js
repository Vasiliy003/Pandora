const start_time = document.querySelector('[name="time"]');
const timer = document.querySelector('#timer')

function dateStringToTimestamp(dateString) {
    const [datePart, timePart] = dateString.split(' ');
    const [day, month, year] = datePart.split('.').map(Number);
    const [hours, minutes, seconds] = timePart.split(':').map(Number);
    
    const date = new Date(year, month - 1, day, hours, minutes, seconds);
    
    return date.getTime();
}

function timerCalc(timestamp) {
    const current_time = Date.now();
    const remain = 30*60000 - (current_time - timestamp);
    const minutes = Math.floor(remain/60000);
    const seconds = Math.floor((remain - minutes*60000)/1000);
    timer.innerText = `${minutes}:${seconds}`
}

const dateStr = start_time.value;
const timestamp = dateStringToTimestamp(dateStr);

let intervalID = setInterval(timerCalc, 1000, timestamp)
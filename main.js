console.log('Hello world!')

const ws = new WebSocket('ws://161.35.144.244:8080')

formChat.addEventListener('submit', (e) => {
    e.preventDefault()
    ws.send(textField.value)
    textField.value = null
})

ws.onopen = (e) => {
    console.log('Hello WebSocket!')
}

ws.onmessage = (e) => {
    console.log(e.data)
    const htmlMessage = e.data;

    const elMsg = document.createElement('div');
    elMsg.innerHTML = htmlMessage;
    subscribe.appendChild(elMsg);
}

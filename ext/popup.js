let intervalId = null
const API_ENDPOINT = 'http://127.0.0.1:5000/api/live-chat'

showLatestTranscript()

document.getElementById('start').addEventListener('click', async () => {
    const tab = await getCurrentTab()
    if(!tab) return alert('Require an active tab')
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content-script.js"]
    })
})

document.getElementById('stop').addEventListener('click', async () => {
    const tab = await getCurrentTab()
    if(!tab) return alert('Require an active tab')
    chrome.tabs.sendMessage(tab.id, { message: 'stop' })
})

document.getElementById('clear').addEventListener('click', async () => {
    chrome.storage.local.remove(['transcript'])
    document.getElementById('transcript').innerHTML = ''
})

document.getElementById('options').addEventListener('click', async () => {
    chrome.runtime.openOptionsPage()
})

chrome.runtime.onMessage.addListener(({ message }) => {
    if(message == 'transcriptavailable') {
        showLatestTranscript()
    }
})

async function showLatestTranscript() {
    const { transcript } = await chrome.storage.local.get("transcript")
    console.log(transcript)
    chrome.storage.local.get("transcript", ({ transcript }) => {
        document.getElementById('transcript').innerHTML = transcript

        // Send transcript data to API endpoint when the length is greater than 100 words
        if (transcript.split(' ').length > 100) {
            sendTranscriptToApi(transcript)
        }
    })
}

function sendTranscriptToApi(transcript) {
    // If there's already an ongoing interval, clear it to avoid overlapping requests
    if (intervalId) clearInterval(intervalId)

    // Send a POST request to API endpoint
    fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ transcript })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to send transcript data to API endpoint')
        }
        console.log('Transcript data sent to API endpoint')
    })
    .catch(error => console.error(error))

    // Set a new interval to send transcript data every 30 seconds
    intervalId = setInterval(() => {
        sendTranscriptToApi(transcript)
    }, 30000)
}

async function getCurrentTab() {
    const queryOptions = { active: true, lastFocusedWindow: true }
    const [tab] = await chrome.tabs.query(queryOptions)
    return tab
}

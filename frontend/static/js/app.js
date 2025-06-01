// WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws/demo`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "comment") {
        document.getElementById("comments").innerHTML += 
            `<div class="comment"><strong>${data.user || 'Anonymous'}:</strong> ${data.text}</div>`;
    }
};

async function analyzeCode() {
    const code = document.getElementById("code").value;
    if (!code) {
        alert("Please enter some code first");
        return;
    }

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        document.getElementById("output").innerHTML = marked.parse(result.suggestions);
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("output").innerHTML = `Error: ${error.message}`;
    }
}

function sendComment() {
    const comment = document.getElementById("comment").value.trim();
    if (!comment) return;
    
    ws.send(JSON.stringify({ 
        type: "comment", 
        text: comment, 
        user: "User" + Math.floor(Math.random() * 1000) 
    }));
    document.getElementById("comment").value = "";
}

// Initialize Markdown parser
const marked = window.marked || {
    parse: (text) => text.replace(/\n/g, "<br>")
};
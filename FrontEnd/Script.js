const chat = document.getElementById("chat");
const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send");


async function sendQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }


    // Remove welcome screen
    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }


    // User message

    const userMessage = document.createElement("div");

    userMessage.className =
        "message user-message";

    userMessage.innerHTML = `
        <div class="user-bubble">
            ${escapeHtml(question)}
        </div>
    `;

    chat.appendChild(userMessage);


    // Clear input

    questionInput.value = "";


    // Loading

    const loading = document.createElement("div");

    loading.className =
        "message ai-message";

    loading.innerHTML = `
        <div class="ai-icon">◈</div>

        <div class="loading">
            Searching the knowledge graph...
        </div>
    `;

    chat.appendChild(loading);

    scrollToBottom();


    try {

        const response = await fetch(
            "http://localhost:8001/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        if (!response.ok) {
            throw new Error("Request failed");
        }


        const data = await response.json();


        loading.remove();


        // Sources

        let sourcesHtml = "";

        if (data.sources && data.sources.length > 0) {

            sourcesHtml = `
                <div class="sources">
                    ${data.sources.map(
                        source => `
                            <div class="source">
                                ${escapeHtml(source)}
                            </div>
                        `
                    ).join("")}
                </div>
            `;
        }


        // AI message

        const aiMessage = document.createElement("div");

        aiMessage.className =
            "message ai-message";

        aiMessage.innerHTML = `
            <div class="ai-icon">◈</div>

            <div>

                <div class="answer">
                    ${escapeHtml(data.answer)}
                </div>

                ${sourcesHtml}

            </div>
        `;


        chat.appendChild(aiMessage);

        scrollToBottom();

    } catch (error) {

        loading.innerHTML =
            "Unable to connect to the GraphRAG backend.";

        console.error(error);

    }

}


function askExample(button) {

    questionInput.value =
        button.innerText;

    sendQuestion();

}


function newChat() {

    location.reload();

}


function scrollToBottom() {

    chat.scrollTop =
        chat.scrollHeight;

}


function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;

}


questionInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendQuestion();

        }

    }
);
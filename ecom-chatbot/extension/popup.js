const welcomeMessage =
  "Hello! I am SaatvaAI, a conversational chatbot. I can answer questions about Saatva products and services. Ask me anything!";

const SERVER_ENDPOINT = "http://127.0.0.1:5000";

let conversation = document.getElementById("conversation");
let userInput = document.getElementById("user-input");
let submitButton = document.getElementById("submit-button");
let clearConversationButton = document.getElementById(
  "clear-conversation-button"
);
let clearInputButton = document.getElementById("clear-input-button");

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM Content Loaded");

  conversation.innerHTML += `<div class="chatbot-message">${welcomeMessage}</div>`;

  userInput.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      submitButton.click();
      clearInputButton.disabled = true;
      submitButton.disabled = true;
    }
  });

  submitButton.addEventListener("click", function () {
    console.log("Submit button clicked");

    clearInputButton.disabled = true;
    submitButton.disabled = true;

    let question = userInput.value;
    conversation.innerHTML += `<div class="user-message">${question}</div>`;
    userInput.value = "";

    // Scroll to the bottom
    conversation.scrollTop = conversation.scrollHeight;

    // Create and append typing indicator to conversation
    let typeIndicator = document.createElement("div");
    typeIndicator.id = "typing-indicator";
    typeIndicator.classList.add("typing-indicator");
    typeIndicator.innerHTML =
      "<span><strong>SaatvaAI: </strong>One moment...</span>";
    conversation.appendChild(typeIndicator);

    // Scroll to show typing indicator
    conversation.scrollTop = conversation.scrollHeight;

    // Get the URL of the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      console.log("Inside chrome.tabs.query");
      let activeTab = tabs[0];
      let activeTabURL = activeTab.url;
      console.log("Active tab URL:", activeTabURL);

      chrome.scripting.executeScript(
        {
          target: { tabId: activeTab.id },
          function: stub,
        },
        (results) => {
          let payload = {
            question: question,
          };

          chat(payload, function (chatbotResponse) {
            // Remove typing indicator
            conversation.removeChild(typeIndicator);

            // Append chatbot's reply to conversation
            conversation.innerHTML += `<div class="chatbot-message"><span class="chatbot-label"><strong>SaatvaAI:</strong></span> ${chatbotResponse}</div>`;

            // Scroll to the bottom again
            conversation.scrollTop = conversation.scrollHeight;
          });
        }
      );
    });
  });
});

clearConversationButton.addEventListener("click", function () {
  console.log("Clear Conversation button clicked");
  conversation.innerHTML = `<div class="chatbot-message">${welcomeMessage}</div>`;
});

clearInputButton.addEventListener("click", function () {
  console.log("Clear Input button clicked");
  userInput.value = "";
  clearInputButton.disabled = true;
  submitButton.disabled = true;
});

document.addEventListener("input", function () {
  console.log("User inputs");
  let clearInputButton = document.getElementById("clear-input-button");
  let submitButton = document.getElementById("submit-button");
  let input = document.getElementById("user-input");
  if (input.value === "") {
    clearInputButton.disabled = true;
    submitButton.disabled = true;
  } else {
    clearInputButton.disabled = false;
    submitButton.disabled = false;
  }
});

function chat(payload, callback) {
  console.log("Inside chat_with_chatbot");
  fetch(`${SERVER_ENDPOINT}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => callback(data.response))
    .catch((error) => console.error("An error occurred:", error));
}

function scrollToBottom() {
  const conversationDiv = document.getElementById("conversation");
  conversationDiv.scrollTop = conversationDiv.scrollHeight;
}

// Scroll to bottom every time a new message is added.
scrollToBottom();

function stub() {}

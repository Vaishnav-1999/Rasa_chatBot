let chatOpened = false;
//let askName = 0;
let userName = "";

document.getElementById("chatIcon").addEventListener("click", function () {
  const chatWindow = document.getElementById("chatWindow");

  if (chatWindow.style.display === "none" || chatWindow.style.display === "") {
    //alert("7")
    chatWindow.style.display = "block";
    if (!chatOpened) {
      waitingMessage();
      chatOpened = true;
      initMessage("Hi");
      //initializeBot();
    }
  } else {
    chatWindow.style.display = "none";
  }
});

function initMessage(intent) {
  let message;
  if (intent === undefined) {
    message = "Hi";
  } else {
    message = intent;
  }

  if (message.trim() !== "") {
    fetch("http://localhost:8081/api/chat/rasa", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.response.includes("Welcome to the LivEzy services")) {
          funOnce();
        } else {
          //alert(Array.isArray(data.response))
          /*if (isJsonString(data.response)) {
						let btnArr = JSON.parse(data.response);
						displayMessage('Lizzy', btnArr);
					}
					else {
						displayMessage('Lizzy', data.response);
					}*/
          if (isJsonString(data.response)) {
            let dataArr = JSON.parse(data.response);
            console.log(data.response);
            displayMessage("Lizzy", dataArr);
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
}

function waitingMessage() {
  const chatBody = document.getElementById("chatBody");
  const messageElement = document.createElement("div");

  let span = document.createElement("span");
  let img = document.createElement("img");
  img.src = "Liv Eze icon.jpg";
  img.alt = "LivEzy Image";
  img.style.width = "35px";
  img.style.height = "20px";
  span.appendChild(img);
  let innerDiv2 = document.createElement("div");
  innerDiv2.style.display = "flex";
  innerDiv2.style.alignItem = "center";
  innerDiv2.appendChild(span);

  const innerDiv = document.createElement("div");

  innerDiv.classList.add("typing-container");
  const messageElement1 = document.createElement("div");
  messageElement1.classList.add("dot");
  const messageElement2 = document.createElement("div");
  messageElement2.classList.add("dot");
  const messageElement3 = document.createElement("div");
  messageElement3.classList.add("dot");
  innerDiv.appendChild(messageElement1);
  innerDiv.appendChild(messageElement2);
  innerDiv.appendChild(messageElement3);
  //innerDiv.textContent = `${message}`;
  innerDiv.classList.add("padded");
  innerDiv.classList.add("bot-message");
  innerDiv.style.fontSize = "14px";
  innerDiv2.appendChild(innerDiv);
  innerDiv2.classList.add("typing-container");
  messageElement.appendChild(innerDiv2);

  /*messageElement.classList.add('typing-container');
	const messageElement1 = document.createElement('div');
	messageElement1.classList.add('dot');
	const messageElement2 = document.createElement('div');
	messageElement2.classList.add('dot');
	const messageElement3 = document.createElement('div');
	messageElement3.classList.add('dot');*/
  //messageElement.appendChild(messageElement1);
  //messageElement.appendChild(messageElement2);
  //messageElement.appendChild(messageElement3);
  chatBody.appendChild(messageElement);
  chatBody.scrollTop = chatBody.scrollHeight;
}
/*function initializeBot() {
	const chatBody = document.getElementById('chatBody');
	const messageElement1 = document.createElement('div');
	const messageElement2 = document.createElement('div');

	messageElement1.classList.add('padded');
	messageElement1.classList.add('bot-message');
	messageElement2.classList.add('padded');
	messageElement2.classList.add('bot-message');
	
	const span = document.createElement('span');
      const img = document.createElement('img');
      img.src = 'images/Liv-Eze-icon.jpg';
      img.alt = 'LivEzy Image';
      img.style.width = '35px';
      img.style.height = '20px';
      span.appendChild(img);
	
	const innerDiv = document.createElement('div');
	innerDiv.style.display = 'flex';
	innerDiv.style.alignItem = 'center';
	innerDiv.appendChild(span);
	innerDiv.appendChild(messageElement1);
	setTimeout(() => {
		messageElement1.textContent = `Hi, I am Lizzy.`;
		chatBody.appendChild(innerDiv);
		chatBody.scrollTop = chatBody.scrollHeight;
	}, 1000);

	const span2 = document.createElement('span');
	const img2 = document.createElement('img');
	img2.src = 'images/Liv-Eze-icon.jpg';
	img2.alt = 'LivEzy Image';
	img2.style.width = '35px';
	img2.style.height = '20px';
	span2.appendChild(img2);
	const innerDiv2 = document.createElement('div');
	innerDiv2.style.display = 'flex';
	innerDiv2.style.alignItem = 'center';
	innerDiv2.appendChild(span2);
	innerDiv2.appendChild(messageElement2);
	setTimeout(() => {
		messageElement2.textContent = `Please enter your name.`;
		chatBody.appendChild(innerDiv2);
		chatBody.scrollTop = chatBody.scrollHeight;
	}, 2000);
}*/

document.getElementById("minWindow").addEventListener("click", function () {
  const chatWindow = document.getElementById("chatWindow");
  chatWindow.style.display = "none";
});

document.getElementById("refreshWindow").addEventListener("click", function () {
  const chatWindow = document.getElementById("chatBody");
  chatWindow.innerHTML = "";
  askName = 0;
  userName = "";
  initializeBot();
});

/*document.getElementById('sendBtn').addEventListener('click', function () {
	alert("button")
	sendMessage();
});*/

document.getElementById("chatInput").addEventListener("keypress", function (e) {
  //alert("Before enter")

  if (e.key === "Enter") {
    sendMessage();
    /*if (askName == 0) {
			sendMessage1();
			askName = 1;
		}
		else {
			sendMessage();
		}*/
  }
});

/*function sendMessage1() {
	const chatInput = document.getElementById('chatInput');
	const message = chatInput.value;
	userName = message;
	displayMessage('You', message);
	chatInput.value = '';
	funOnce();
}
function funOnce() {
	//displayMessage('Lizzy', `${userName}, Please choose from option below.1. Order Status`);
	var firstBtn = [{ "text": "", "buttons": [{ "title": "Orders", "payload": "fa fa-reorder" }, { "title": "Flight Status", "payload": "fas fa-plane" }, { "title": "Home Services", "payload": "/homeServices" }] }];
	setTimeout(() => {
		displayMessage('Lizzy', `${userName}, Please choose from option below.`);
	}, 1000);
	setTimeout(() => {
		displayMessage('', firstBtn);
	}, 1000);
}*/
function sendMessage(intent) {
  const chatInput = document.getElementById("chatInput");
  //const message = intent === 'start' ? 'start' : chatInput.value;
  let message;
  if (intent === undefined) {
    message = chatInput.value;
  } else {
    message = intent;
  }

  //alert(message)
  if (message.trim() !== "") {
    //if (intent !== 'start') {
    displayMessage("You", message);
    chatInput.value = "";
    //}
    // Call Spring Boot API
    fetch("http://localhost:8081/api/chat/rasa", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.response.includes("Welcome to the LivEzy services")) {
          funOnce();
        } else {
          //alert(Array.isArray(data.response))
          /*if (isJsonString(data.response)) {
						let btnArr = JSON.parse(data.response);
						displayMessage('Lizzy', btnArr);
					}
					else {
						displayMessage('Lizzy', data.response);
					}*/
          if (isJsonString(data.response)) {
            let dataArr = JSON.parse(data.response);
            console.log(data.response);
            displayMessage("Lizzy", dataArr);
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
    /*fetch('http://localhost:8081/api/chat/testing')
			.then(response => response.text())
			.then(data => {
				document.getElementById('responseData').innerText = data;
			})
			.catch(error => console.error('Error:', error));*/
  }
}

function displayMessage(sender, rootMessage) {
  //alert(JSON.stringify(rootMessage))

  const elements = document.querySelectorAll(".typing-container");
  elements.forEach((element) => {
    element.remove();
  });

  const chatBody = document.getElementById("chatBody");
  const messageElement = document.createElement("div");
  if (Array.isArray(rootMessage)) {
    for (let a = 0; a < rootMessage.length; a++) {
      let rootObj = rootMessage[a];
      //alert("it's an array : " + ('text' in rootObj));
      if ("text" in rootObj) {
        let message = rootObj.text;
        if (message.length > 0) {
          let span = document.createElement("span");
          let img = document.createElement("img");
          img.src = "/Liv Eze icon.jpg";
          img.alt = "LivEzy Image";
          img.style.width = "35px";
          img.style.height = "20px";
          span.appendChild(img);
          let innerDiv2 = document.createElement("div");
          innerDiv2.style.display = "flex";
          innerDiv2.style.alignItem = "center";
          innerDiv2.appendChild(span);

          const innerDiv = document.createElement("div");
          innerDiv.textContent = `${message}`;
          innerDiv.classList.add("padded");
          innerDiv.classList.add("bot-message");
          innerDiv2.appendChild(innerDiv);
          messageElement.appendChild(innerDiv2);
        }
      }
      if ("buttons" in rootObj) {
        let btnArr = rootObj.buttons;
        for (let b = 0; b < btnArr.length; b++) {
          const button = document.createElement("button");
          button.textContent = btnArr[b].title;
          button.id = btnArr[b].payload;
          button.className = "btn";
          button.style.color = "black";
          button.style.backgroundColor = "#fff";

          button.style.border = "1.2px solid grey";
          button.style.padding = "8px 15px";
          button.style.fontSize = "12px";
          button.style.margin = "2px";
          button.style.cursor = "pointer";
          button.style.borderRadius = "15px";
          button.addEventListener("click", () => {
            //alert('Button was clicked!');
            botButtonClick(btnArr[b].title);
          });
          button.addEventListener("mouseover", () => {
            button.style.backgroundColor = "rgb(198, 255, 255)"; // Light gray background on hover
          });

          button.addEventListener("mouseout", () => {
            button.style.backgroundColor = "#fff"; // White background when not hovered
          });

          messageElement.appendChild(button);
          console.log(messageElement);
        }
      }
    }
  } else {
    if (sender.localeCompare("Lizzy") != 0) {
      messageElement.textContent = `${sender}: ${rootMessage}`;
      messageElement.classList.add("padded");
      messageElement.classList.add("user-message");
    } else {
      let span = document.createElement("span");
      let img = document.createElement("img");
      img.src = "/Liv Eze icon.jpg";
      img.alt = "LivEzy Image";
      img.style.width = "35px";
      img.style.height = "20px";
      span.appendChild(img);
      let innerDiv2 = document.createElement("div");
      innerDiv2.style.display = "flex";
      innerDiv2.style.alignItem = "center";
      innerDiv2.appendChild(span);
      let innerDiv = document.createElement("div");
      //messageElement.textContent = `${sender}: ${rootMessage}`;
      innerDiv.textContent = `${rootMessage}`;
      innerDiv.classList.add("padded");
      innerDiv.classList.add("bot-message");
      innerDiv2.appendChild(innerDiv);
      //messageElement.classList.add('padded');
      //messageElement.classList.add('bot-message');
      messageElement.appendChild(innerDiv2);
    }
  }

  chatBody.appendChild(messageElement);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function botButtonClick(btnName) {
  //alert("button clicked....")
  //alert(btnName)
  sendMessage(btnName);
}

/*document.querySelector('.refresh-button').addEventListener('click', function() {
	location.reload();
});*/

document
  .querySelector(".minimize-button")
  .addEventListener("click", function () {
    const container = document.querySelector(".container");
    if (container.style.display !== "none") {
      container.style.display = "none";
    } else {
      container.style.display = "flex";
    }
  });

function isJsonString(str) {
  try {
    // Try to parse the string to JSON
    let parsed = JSON.parse(str);

    // Check if the parsed result is an array
    if (Array.isArray(parsed)) {
      return true;
    } else {
      return false;
    }
  } catch (e) {
    // If parsing throws an error, it is not valid JSON
    return false;
  }
}

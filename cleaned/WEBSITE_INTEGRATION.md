# Website Integration Guide for Nexobotics RAG Chatbot

This guide explains how to integrate the Nexobotics RAG Chatbot into your website.

## Table of Contents

1. [Basic Integration](#basic-integration)
2. [Advanced Configuration](#advanced-configuration)
3. [Styling and Customization](#styling-and-customization)
4. [Event Handling](#event-handling)
5. [Integration Examples](#integration-examples)

## Basic Integration

Integrating the chatbot widget into your website requires just a few simple steps:

### Step 1: Add the Script to Your HTML

Add the following script tag to your website, preferably just before the closing `</body>` tag:

```html
<script src="path/to/chatbot.js"></script>
```

Replace `path/to/chatbot.js` with the actual path to the chatbot.js file on your server.

### Step 2: Initialize the Chatbot

Add this script after the previous one:

```html
<script>
  document.addEventListener("DOMContentLoaded", function () {
    // Initialize the chatbot
    const chatbot = new NexoboticsChat({
      serverUrl: "http://your-server-url:5000/chat",
      position: "bottom-right",
      initialMessage: "How can I assist you today?",
    });
  });
</script>
```

Replace `http://your-server-url:5000/chat` with the actual URL where your chatbot server is running.

### Step 3: Test the Integration

Open your website and you should see the chat icon in the bottom-right corner of the page. Click it to open the chat interface.

## Advanced Configuration

The chatbot constructor accepts several configuration options:

```javascript
const chatbot = new NexoboticsChat({
  // Required
  serverUrl: "http://your-server-url:5000/chat",

  // Optional with defaults
  position: "bottom-right", // Possible values: 'bottom-right', 'bottom-left'
  initialMessage: "How can I assist you today?",
  logoUrl: "path/to/logo.png",
  title: "Nexobotics Support",
  placeholder: "Type your message here...",
  primaryColor: "#0078d7",
  secondaryColor: "#f5f5f5",
  textColor: "#333333",
  showStarterQuestions: true,
  starterQuestions: [
    "What services do you offer?",
    "How can I contact support?",
    "What are your business hours?",
  ],
});
```

### Configuration Options

| Option                 | Type    | Default                       | Description                          |
| ---------------------- | ------- | ----------------------------- | ------------------------------------ |
| `serverUrl`            | String  | _Required_                    | URL of the chat API endpoint         |
| `position`             | String  | 'bottom-right'                | Position of the chat widget          |
| `initialMessage`       | String  | 'How can I assist you today?' | First message from the bot           |
| `logoUrl`              | String  | (Default logo)                | URL to your company logo             |
| `title`                | String  | 'Nexobotics Support'          | Title displayed in the chat header   |
| `placeholder`          | String  | 'Type your message here...'   | Placeholder text for the input field |
| `primaryColor`         | String  | '#0078d7'                     | Primary color for the chat theme     |
| `secondaryColor`       | String  | '#f5f5f5'                     | Background color for the chat        |
| `textColor`            | String  | '#333333'                     | Color for the text content           |
| `showStarterQuestions` | Boolean | true                          | Whether to show starter questions    |
| `starterQuestions`     | Array   | []                            | List of starter questions to display |

## Styling and Customization

### Custom CSS

You can override the default styles by adding your own CSS after the chatbot is initialized:

```html
<style>
  .nexobotics-chat-container {
    /* Your custom styles */
    font-family: "Your Custom Font", sans-serif;
  }

  .nexobotics-chat-header {
    background-color: #your-brand-color;
  }

  /* More custom styles */
</style>
```

### Custom Logo and Branding

To use your own logo and brand colors:

```javascript
const chatbot = new NexoboticsChat({
  serverUrl: "http://your-server-url:5000/chat",
  logoUrl: "https://your-website.com/logo.png",
  primaryColor: "#your-brand-color",
  title: "Your Company Support",
});
```

## Event Handling

The chatbot provides several events you can hook into:

```javascript
const chatbot = new NexoboticsChat({
  serverUrl: "http://your-server-url:5000/chat",
});

// Listen for when the chat widget opens
chatbot.on("open", function () {
  console.log("Chat widget opened");
});

// Listen for when the chat widget closes
chatbot.on("close", function () {
  console.log("Chat widget closed");
});

// Listen for when a message is sent
chatbot.on("messageSent", function (message) {
  console.log("User sent a message:", message);
});

// Listen for when a response is received
chatbot.on("responseReceived", function (response) {
  console.log("Bot response:", response);
});
```

### Available Events

| Event              | Description                                           |
| ------------------ | ----------------------------------------------------- |
| `open`             | Triggered when the chat widget opens                  |
| `close`            | Triggered when the chat widget closes                 |
| `messageSent`      | Triggered when the user sends a message               |
| `responseReceived` | Triggered when a response is received from the server |
| `error`            | Triggered when an error occurs                        |

## Integration Examples

### Basic Website Integration

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Your Website</title>
  </head>
  <body>
    <!-- Your website content here -->

    <script src="path/to/chatbot.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", function () {
        const chatbot = new NexoboticsChat({
          serverUrl: "http://your-server-url:5000/chat",
          title: "Customer Support",
          initialMessage: "Hello! How can I help you today?",
        });
      });
    </script>
  </body>
</html>
```

### Integration with Analytics

```html
<script src="path/to/chatbot.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    const chatbot = new NexoboticsChat({
      serverUrl: "http://your-server-url:5000/chat",
    });

    // Track chat interactions
    chatbot.on("open", function () {
      // Google Analytics example
      gtag("event", "chat_open", {
        event_category: "Chat",
        event_label: "Widget Opened",
      });
    });

    chatbot.on("messageSent", function (message) {
      gtag("event", "chat_message", {
        event_category: "Chat",
        event_label: "Message Sent",
      });
    });
  });
</script>
```

### Programmatic Control

You can control the chatbot programmatically:

```javascript
const chatbot = new NexoboticsChat({
  serverUrl: "http://your-server-url:5000/chat",
});

// Open the chat widget
document
  .getElementById("support-button")
  .addEventListener("click", function () {
    chatbot.open();
  });

// Send a predefined message
document.getElementById("pricing-help").addEventListener("click", function () {
  chatbot.open();
  chatbot.sendMessage("I need help with pricing");
});

// Close the chat widget
document.getElementById("close-support").addEventListener("click", function () {
  chatbot.close();
});
```

## Troubleshooting

If you encounter issues:

1. Check the browser console for errors
2. Verify that the server URL is correct and accessible
3. Ensure that CORS is properly configured on the server
4. Test the server independently using API testing tools

For additional help, refer to the project documentation or contact the development team.

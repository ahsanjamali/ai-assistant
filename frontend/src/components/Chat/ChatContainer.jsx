import { useState } from "react";
import { Box, Paper, TextField, Button, Typography } from "@mui/material";
import { alpha } from "@mui/material/styles";

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    // Add user message to chat
    const userMessage = { text: inputMessage, isUser: true };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      // Add assistant's response to chat
      const assistantMessage = { text: data.content, isUser: false };
      setMessages((prev) => [...prev, assistantMessage]);

      // Trigger dashboard update if the response indicates a task/meeting modification
      if (
        data.content.includes("Task added:") ||
        data.content.includes("Meeting scheduled:") ||
        data.content.includes("Marked task") ||
        data.content.includes("Deleted task") ||
        data.content.includes("Deleted meeting")
      ) {
        // Dispatch custom event to trigger dashboard refresh
        window.dispatchEvent(new CustomEvent("dashboardUpdate"));
      }
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        text: "Error: Failed to fetch response",
        isUser: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Paper
      sx={{
        height: "80vh",
        display: "flex",
        flexDirection: "column",
        p: 3,
        bgcolor: "#fafafa",
        borderRadius: 2,
        boxShadow: 3,
      }}
    >
      <Box sx={{ flexGrow: 1, overflow: "auto", mb: 2 }}>
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: "flex",
              justifyContent: message.isUser ? "flex-end" : "flex-start",
              mb: 2,
              position: "relative",
            }}
          >
            <Box
              sx={{
                maxWidth: "70%",
                p: 2,
                bgcolor: message.isUser ? alpha("#1976d2", 0.9) : "#fff",
                color: message.isUser ? "#fff" : "text.primary",
                borderRadius: message.isUser
                  ? "20px 20px 5px 20px"
                  : "20px 20px 20px 5px",
                boxShadow: 1,
                position: "relative",
                overflowY: "auto",
                maxHeight: "200px",
                "&::-webkit-scrollbar": {
                  width: "8px",
                },
                "&::-webkit-scrollbar-track": {
                  background: "transparent",
                },
                "&::-webkit-scrollbar-thumb": {
                  background: alpha("#1976d2", 0.2),
                  borderRadius: "4px",
                },
                "&::-webkit-scrollbar-thumb:hover": {
                  background: alpha("#1976d2", 0.3),
                },
                "&::after": {
                  content: '""',
                  position: "absolute",
                  bottom: 0,
                  [message.isUser ? "right" : "left"]: -8,
                  width: 0,
                  height: 0,
                  borderStyle: "solid",
                  borderWidth: message.isUser ? "0 0 8px 8px" : "0 8px 8px 0",
                  borderColor: message.isUser
                    ? `transparent transparent transparent ${alpha(
                        "#1976d2",
                        0.9
                      )}`
                    : "transparent #fff transparent transparent",
                },
              }}
            >
              <Typography variant="body1" sx={{ wordBreak: "break-word" }}>
                {message.text}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
      <Box
        sx={{
          display: "flex",
          gap: 1,
          p: 2,
          bgcolor: "#fff",
          borderRadius: 2,
          boxShadow: 1,
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          size="small"
          sx={{
            "& .MuiOutlinedInput-root": {
              borderRadius: 3,
              "&.Mui-focused fieldset": {
                borderColor: "primary.main",
                borderWidth: 2,
              },
            },
          }}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!inputMessage.trim()}
          sx={{
            borderRadius: 3,
            px: 3,
            textTransform: "none",
            "&:hover": {
              bgcolor: "primary.dark",
            },
          }}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default ChatContainer;

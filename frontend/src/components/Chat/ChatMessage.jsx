import PropTypes from "prop-types";
import { Box, Paper, Typography } from "@mui/material";

const ChatMessage = ({ message, isUser }) => {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        mb: 2,
      }}
    >
      <Paper
        sx={{
          p: 2,
          maxWidth: "70%",
          backgroundColor: isUser ? "#e3f2fd" : "#fff",
          borderRadius: "1rem",
        }}
      >
        <Typography variant="body1">{message}</Typography>
      </Paper>
    </Box>
  );
};

ChatMessage.propTypes = {
  message: PropTypes.string.isRequired,
  isUser: PropTypes.bool.isRequired,
};

export default ChatMessage;

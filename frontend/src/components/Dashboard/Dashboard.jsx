import { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Checkbox,
  IconButton,
  CircularProgress,
  Alert,
  Tooltip,
  alpha,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EventIcon from "@mui/icons-material/Event";
import TaskAltIcon from "@mui/icons-material/TaskAlt";
import { format } from "date-fns";

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [tasksResponse, meetingsResponse] = await Promise.all([
        fetch("http://localhost:8000/api/tasks"),
        fetch("http://localhost:8000/api/meetings"),
      ]);

      if (!tasksResponse.ok || !meetingsResponse.ok) {
        throw new Error("Failed to fetch data");
      }

      const tasksData = await tasksResponse.json();
      const meetingsData = await meetingsResponse.json();

      setTasks(tasksData.tasks);
      setMeetings(meetingsData.meetings);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteTask = async (taskId) => {
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: `complete task ${tasks.find((t) => t.id === taskId)?.title}`,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to complete task");
      }

      // Refresh the dashboard
      fetchData();
    } catch (error) {
      console.error("Error completing task:", error);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: `delete task ${tasks.find((t) => t.id === taskId)?.title}`,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to delete task");
      }

      // Refresh the dashboard
      fetchData();
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  const handleDeleteMeeting = async (meetingId) => {
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: `delete meeting ${
            meetings.find((m) => m.id === meetingId)?.title
          }`,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to delete meeting");
      }

      // Refresh the dashboard
      fetchData();
    } catch (error) {
      console.error("Error deleting meeting:", error);
    }
  };

  useEffect(() => {
    fetchData();
    // Listen for updates from chat
    window.addEventListener("dashboardUpdate", fetchData);
    return () => window.removeEventListener("dashboardUpdate", fetchData);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        gap: 3,
        height: "100%",
        overflow: "auto",
      }}
    >
      {/* Tasks Section */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          borderRadius: 4,
          border: "1px solid",
          borderColor: "divider",
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            p: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            background: (theme) => alpha(theme.palette.primary.main, 0.03),
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          <TaskAltIcon color="primary" />
          <Typography variant="h6" color="primary.main">
            Tasks
          </Typography>
        </Box>
        <List sx={{ p: 0 }}>
          {tasks.length > 0 ? (
            tasks.map((task) => (
              <ListItem
                key={task.id}
                sx={{
                  borderBottom: "1px solid",
                  borderColor: "divider",
                  "&:last-child": { borderBottom: "none" },
                  transition: "all 0.2s",
                  "&:hover": {
                    bgcolor: (theme) => alpha(theme.palette.primary.main, 0.03),
                  },
                }}
              >
                <ListItemIcon>
                  <Tooltip
                    title={
                      task.completed ? "Task completed" : "Mark as complete"
                    }
                  >
                    <Checkbox
                      edge="start"
                      checked={task.completed}
                      onChange={() =>
                        !task.completed && handleCompleteTask(task.id)
                      }
                      sx={{
                        color: "primary.main",
                        "&.Mui-checked": {
                          color: "primary.main",
                        },
                      }}
                    />
                  </Tooltip>
                </ListItemIcon>
                <ListItemText
                  primary={task.title}
                  secondary={format(new Date(task.created_at), "MMM d, yyyy")}
                  sx={{
                    textDecoration: task.completed ? "line-through" : "none",
                    opacity: task.completed ? 0.7 : 1,
                  }}
                />
                <ListItemSecondaryAction>
                  <Tooltip title="Delete task">
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteTask(task.id)}
                      sx={{
                        color: "grey.500",
                        "&:hover": { color: "error.main" },
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
            ))
          ) : (
            <ListItem>
              <ListItemText
                primary="No tasks yet"
                sx={{ color: "text.secondary", textAlign: "center" }}
              />
            </ListItem>
          )}
        </List>
      </Paper>

      {/* Meetings Section */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          borderRadius: 4,
          border: "1px solid",
          borderColor: "divider",
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            p: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            background: (theme) => alpha(theme.palette.primary.main, 0.03),
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          <EventIcon color="primary" />
          <Typography variant="h6" color="primary.main">
            Meetings
          </Typography>
        </Box>
        <List sx={{ p: 0 }}>
          {meetings.length > 0 ? (
            meetings.map((meeting) => (
              <ListItem
                key={meeting.id}
                sx={{
                  borderBottom: "1px solid",
                  borderColor: "divider",
                  "&:last-child": { borderBottom: "none" },
                  transition: "all 0.2s",
                  "&:hover": {
                    bgcolor: (theme) => alpha(theme.palette.primary.main, 0.03),
                  },
                }}
              >
                <ListItemText
                  primary={meeting.title}
                  secondary={
                    <>
                      {format(
                        new Date(meeting.start_time),
                        "MMM d, yyyy h:mm a"
                      )}
                      <br />
                      {format(new Date(meeting.end_time), "h:mm a")}
                    </>
                  }
                />
                <ListItemSecondaryAction>
                  <Tooltip title="Delete meeting">
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteMeeting(meeting.id)}
                      sx={{
                        color: "grey.500",
                        "&:hover": { color: "error.main" },
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
            ))
          ) : (
            <ListItem>
              <ListItemText
                primary="No meetings scheduled"
                sx={{ color: "text.secondary", textAlign: "center" }}
              />
            </ListItem>
          )}
        </List>
      </Paper>
    </Box>
  );
};

export default Dashboard;

import { Container, Grid } from "@mui/material";
import ChatContainer from "./components/Chat/ChatContainer";
import Dashboard from "./components/Dashboard/Dashboard";

function App() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <ChatContainer />
        </Grid>
        <Grid item xs={12} md={6}>
          <Dashboard />
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;

import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Box, Button, useColorMode, useColorModeValue } from "@chakra-ui/react";
import { MoonIcon, SunIcon } from '@chakra-ui/icons';
import { useAuth } from "./hooks/useAuth.jsx";
import LoginForm from "./components/Auth/LoginForm.jsx";
import RegisterForm from "./components/Auth/RegisterForm.jsx";
import Home from "./components/Home.jsx";
import NewEntry from "./components/NewEntry.jsx";
import Archive from "./components/Archive.jsx";
import Statistics from "./components/Statistics.jsx";
import TestRAG from "./components/TestRAG.jsx";

// Dark Mode Toggle Component
function DarkModeToggle() {
  const { colorMode, toggleColorMode } = useColorMode();
  return (
    <Button
      position="fixed"
      top={4}
      right={4}
      onClick={toggleColorMode}
      size="sm"
      borderRadius="full"
      zIndex={1000}
    >
      {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
    </Button>
  );
}



export default function App() {
  const { isAuthenticated } = useAuth();
  const bg = useColorModeValue('gray.50', 'gray.900');

  return (
    <Router>
      <Box minH="100vh" bg={bg} transition="all 0.2s">
        <DarkModeToggle />
        <Routes>
          <Route path="/" element={isAuthenticated ? <Home /> : <Navigate to="/login" />} />
          <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <LoginForm />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/" /> : <RegisterForm />} />
          <Route path="/new-entry" element={isAuthenticated ? <NewEntry /> : <Navigate to="/login" />} />
          <Route path="/archive" element={isAuthenticated ? <Archive /> : <Navigate to="/login" />} />
          <Route path="/stats" element={isAuthenticated ? <Statistics /> : <Navigate to="/login" />} />
          <Route path="/test-rag" element={isAuthenticated ? <TestRAG /> : <Navigate to="/login" />} />
          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </Box>
    </Router>
  );
}

import { useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Input,
  Button,
  Link,
  Alert,
  AlertIcon,
  InputGroup,
  InputRightElement,
  IconButton,
  useColorModeValue,
} from "@chakra-ui/react";
import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import { useAuth } from "../../hooks/useAuth.jsx";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    
    try {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Giriş başarısız");
      }
      
      const data = await res.json();
      login(data.access_token);
      navigate("/");
    } catch (err) {
      setError(err.message || "Giriş başarısız. Bilgileri kontrol edin.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.sm" py={8}>
      <VStack spacing={8} align="center">
        <VStack spacing={2} textAlign="center">
          <Heading 
            size="2xl" 
            bgGradient="linear(to-r, brand.500, purple.500)" 
            bgClip="text"
          >
            Mind Mirror
          </Heading>
          <Text fontSize="lg" color="gray.600">
            Hesabınıza giriş yapın
          </Text>
        </VStack>

        <Box 
          w="full" 
          maxW="md" 
          p={8} 
          bg={bg} 
          borderRadius="xl" 
          boxShadow="lg"
          border="1px"
          borderColor={borderColor}
        >
          {error && (
            <Alert status="error" mb={4} borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel htmlFor="email">E-posta</FormLabel>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ornek@email.com"
                  size="lg"
                  disabled={isLoading}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel htmlFor="password">Şifre</FormLabel>
                <InputGroup size="lg">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Şifrenizi girin"
                    disabled={isLoading}
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showPassword ? "Şifreyi gizle" : "Şifreyi göster"}
                      icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                      onClick={() => setShowPassword(!showPassword)}
                      variant="ghost"
                      size="sm"
                    />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <Button
                type="submit"
                colorScheme="brand"
                size="lg"
                w="full"
                isLoading={isLoading}
                loadingText="Giriş yapılıyor..."
              >
                Giriş Yap
              </Button>
            </VStack>
          </form>

          <VStack spacing={4} mt={6}>
            <Text fontSize="sm" color="gray.600" textAlign="center">
              Henüz hesabınız yok mu?{" "}
              <Link as={RouterLink} to="/register" color="brand.500" fontWeight="medium">
                Kayıt Ol
              </Link>
            </Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
}

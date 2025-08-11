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

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    // Şifre kontrolü
    if (formData.password !== formData.confirmPassword) {
      setError("Şifreler eşleşmiyor");
      setIsLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError("Şifre en az 6 karakter olmalıdır");
      setIsLoading(false);
      return;
    }
    
    try {
      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        }),
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Kayıt başarısız");
      }
      
      const data = await res.json();
      setSuccess("Kayıt başarılı! Giriş yapılıyor...");
      
      // Otomatik giriş yap
      setTimeout(() => {
        login(data.access_token);
        navigate("/");
      }, 1500);
      
    } catch (err) {
      setError(err.message || "Kayıt başarısız. Lütfen tekrar deneyin.");
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
            Zihin Aynası
          </Heading>
          <Text fontSize="lg" color="gray.600">
            Yeni hesap oluşturun
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

          {success && (
            <Alert status="success" mb={4} borderRadius="md">
              <AlertIcon />
              {success}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel htmlFor="name">Ad Soyad</FormLabel>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Adınız ve soyadınız"
                  size="lg"
                  disabled={isLoading}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel htmlFor="email">E-posta</FormLabel>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
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
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="En az 6 karakter"
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

              <FormControl isRequired>
                <FormLabel>Şifre Tekrar</FormLabel>
                <InputGroup size="lg">
                  <Input
                    name="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="Şifrenizi tekrar girin"
                    disabled={isLoading}
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showConfirmPassword ? "Şifreyi gizle" : "Şifreyi göster"}
                      icon={showConfirmPassword ? <ViewOffIcon /> : <ViewIcon />}
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
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
                loadingText="Kayıt olunuyor..."
              >
                Kayıt Ol
              </Button>
            </VStack>
          </form>

          <VStack spacing={4} mt={6}>
            <Text fontSize="sm" color="gray.600" textAlign="center">
              Zaten hesabınız var mı?{" "}
              <Link as={RouterLink} to="/login" color="brand.500" fontWeight="medium">
                Giriş Yap
              </Link>
            </Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
} 
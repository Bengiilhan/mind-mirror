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
  HStack,
  Divider,
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
    <Box
      minH="100vh"
      bg="white"
      position="relative"
      overflow="hidden"
    >
      {/* Üst kısımda renkli gradient band */}
      <Box
        position="absolute"
        top="0"
        left="0"
        w="100%"
        h="40%"
        bgGradient="linear(to-br, blue.100, purple.100, pink.100)"
        opacity="0.3"
      />
      
      {/* Sol tarafta büyük daire */}
      <Box
        position="absolute"
        top="20%"
        left="-10%"
        w="300px"
        h="300px"
        bg="purple.200"
        borderRadius="full"
        opacity="0.1"
      />
      
      {/* Sağ tarafta büyük daire */}
      <Box
        position="absolute"
        bottom="10%"
        right="-15%"
        w="400px"
        h="400px"
        bg="blue.200"
        borderRadius="full"
        opacity="0.1"
      />
      
      {/* Ortada küçük daire */}
      <Box
        position="absolute"
        top="50%"
        left="50%"
        transform="translate(-50%, -50%)"
        w="200px"
        h="200px"
        bg="pink.200"
        borderRadius="full"
        opacity="0.05"
      />
      
      {/* Üst köşelerde küçük üçgenler */}
      <Box
        position="absolute"
        top="0"
        left="0"
        w="0"
        h="0"
        borderStyle="solid"
        borderWidth="0 100px 100px 0"
        borderColor="transparent blue.300 transparent transparent"
        opacity="0.1"
      />
      
      <Box
        position="absolute"
        top="0"
        right="0"
        w="0"
        h="0"
        borderStyle="solid"
        borderWidth="0 0 100px 100px"
        borderColor="transparent transparent purple.300 transparent"
        opacity="0.1"
      />

      <Container maxW="container.sm" py={8} position="relative" zIndex={1}>
        <VStack spacing={8} align="center">
          <VStack spacing={4} textAlign="center">
            <Heading 
              size="2xl" 
              bgGradient="linear(to-r, blue.500, purple.600, pink.500)" 
              bgClip="text"
              fontWeight="bold"
              letterSpacing="tight"
            >
              Mind Mirror
            </Heading>
            <Text 
              fontSize="xl" 
              color="gray.600" 
              fontWeight="medium"
              maxW="md"
            >
              Zihninizin aynasına hoş geldiniz ✨
            </Text>
            <Text fontSize="lg" color="gray.500">
              Yeni hesap oluşturun
            </Text>
          </VStack>

          <Box 
            w="full" 
            maxW="md" 
            p={8} 
            bg="rgba(255, 255, 255, 0.95)"
            borderRadius="2xl" 
            boxShadow="2xl"
            border="1px"
            borderColor="gray.200"
            backdropFilter="blur(10px)"
            position="relative"
            _hover={{
              transform: "translateY(-2px)",
              transition: "all 0.3s ease"
            }}
          >
            {/* Üst dekoratif çizgi */}
            <Box
              position="absolute"
              top="0"
              left="50%"
              transform="translateX(-50%)"
              w="60px"
              h="4px"
              bgGradient="linear(to-r, blue.400, purple.500, pink.400)"
              borderRadius="full"
            />

            {error && (
              <Alert status="error" mb={6} borderRadius="xl" variant="subtle">
                <AlertIcon />
                {error}
              </Alert>
            )}

            {success && (
              <Alert status="success" mb={6} borderRadius="xl" variant="subtle">
                <AlertIcon />
                {success}
              </Alert>
            )}

            <form onSubmit={handleSubmit}>
              <VStack spacing={6}>
                <FormControl isRequired>
                  <FormLabel htmlFor="name" fontSize="md" fontWeight="semibold" color="gray.700">
                    Ad Soyad
                  </FormLabel>
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Adınız ve soyadınız"
                    size="lg"
                    disabled={isLoading}
                    borderRadius="xl"
                    border="2px"
                    borderColor="gray.200"
                    _focus={{
                      borderColor: "blue.400",
                      boxShadow: "0 0 0 1px rgba(66, 153, 225, 0.6)"
                    }}
                    _hover={{
                      borderColor: "blue.300"
                    }}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel htmlFor="email" fontSize="md" fontWeight="semibold" color="gray.700">
                    E-posta
                  </FormLabel>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="ornek@email.com"
                    size="lg"
                    disabled={isLoading}
                    borderRadius="xl"
                    border="2px"
                    borderColor="gray.200"
                    _focus={{
                      borderColor: "purple.400",
                      boxShadow: "0 0 0 1px rgba(128, 90, 213, 0.6)"
                    }}
                    _hover={{
                      borderColor: "purple.300"
                    }}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel htmlFor="password" fontSize="md" fontWeight="semibold" color="gray.700">
                    Şifre
                  </FormLabel>
                  <InputGroup size="lg">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="En az 6 karakter"
                      disabled={isLoading}
                      borderRadius="xl"
                      border="2px"
                      borderColor="gray.200"
                      _focus={{
                        borderColor: "pink.400",
                        boxShadow: "0 0 0 1px rgba(236, 72, 153, 0.6)"
                      }}
                      _hover={{
                        borderColor: "pink.300"
                      }}
                    />
                    <InputRightElement>
                      <IconButton
                        aria-label={showPassword ? "Şifreyi gizle" : "Şifreyi göster"}
                        icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                        onClick={() => setShowPassword(!showPassword)}
                        variant="ghost"
                        size="sm"
                        color="gray.500"
                        _hover={{ color: "pink.500" }}
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel fontSize="md" fontWeight="semibold" color="gray.700">
                    Şifre Tekrar
                  </FormLabel>
                  <InputGroup size="lg">
                    <Input
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="Şifrenizi tekrar girin"
                      disabled={isLoading}
                      borderRadius="xl"
                      border="2px"
                      borderColor="gray.200"
                      _focus={{
                        borderColor: "purple.400",
                        boxShadow: "0 0 0 1px rgba(128, 90, 213, 0.6)"
                      }}
                      _hover={{
                        borderColor: "purple.300"
                      }}
                    />
                    <InputRightElement>
                      <IconButton
                        aria-label={showConfirmPassword ? "Şifreyi gizle" : "Şifreyi göster"}
                        icon={showConfirmPassword ? <ViewOffIcon /> : <ViewIcon />}
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        variant="ghost"
                        size="sm"
                        color="gray.500"
                        _hover={{ color: "purple.500" }}
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <Button
                  type="submit"
                  bgGradient="linear(to-r, blue.500, purple.600)"
                  color="white"
                  size="lg"
                  w="full"
                  isLoading={isLoading}
                  loadingText="Kayıt olunuyor..."
                  borderRadius="xl"
                  fontWeight="bold"
                  fontSize="lg"
                  py={7}
                  _hover={{
                    bgGradient: "linear(to-r, blue.600, purple.700)",
                    transform: "translateY(-1px)",
                    boxShadow: "lg"
                  }}
                  _active={{
                    transform: "translateY(0)"
                  }}
                  _focus={{
                    boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.6)"
                  }}
                >
                  Kayıt Ol
                </Button>
              </VStack>
            </form>

            <VStack spacing={4} mt={8}>
              <HStack w="full" spacing={4}>
                <Divider />
                <Text fontSize="sm" color="gray.400" whiteSpace="nowrap">
                  veya
                </Text>
                <Divider />
              </HStack>
              
              <Text fontSize="sm" color="gray.600" textAlign="center">
                Zaten hesabınız var mı?{" "}
                <Link 
                  as={RouterLink} 
                  to="/login" 
                  color="purple.500" 
                  fontWeight="semibold"
                  _hover={{
                    color: "purple.600",
                    textDecoration: "underline"
                  }}
                >
                  Giriş Yap
                </Link>
              </Text>
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
} 
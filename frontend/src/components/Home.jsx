import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  Button,
  useColorModeValue,
  HStack,
  IconButton,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Spinner,
  Alert,
  AlertIcon,
  SimpleGrid,
  Flex,
} from "@chakra-ui/react";
import { AddIcon, CalendarIcon, TimeIcon, ViewIcon, ExternalLinkIcon } from "@chakra-ui/icons";
import { useAuth } from "../hooks/useAuth.jsx";
import { FaRegSadTear, FaRegMeh, FaRegSmile, FaSmileBeam, FaRegFrown } from "react-icons/fa";

export default function Home() {
  const [entries, setEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const { logout } = useAuth();
  const navigate = useNavigate();

  const bg = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const fetchEntries = useCallback(async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/entries/", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json", // bu da önemli
        },

      });


      if (res.status === 401) {
        logout();
        navigate("/login");
        return;
      }

      if (!res.ok) {
        throw new Error("Girişler yüklenemedi");
      }

      const data = await res.json();

      setEntries(data.slice(0, 5)); // Son 5 girişi göster
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [logout, navigate]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const moodIcons = {
    1: { icon: <FaRegFrown />, color: "blue.400", label: "Çok üzgün" },
    2: { icon: <FaRegSadTear />, color: "cyan.400", label: "Üzgün" },
    3: { icon: <FaRegMeh />, color: "gray.400", label: "Nötr" },
    4: { icon: <FaRegSmile />, color: "green.400", label: "Mutlu" },
    5: { icon: <FaSmileBeam />, color: "yellow.400", label: "Çok mutlu" },
  };

  if (isLoading) {
    return (
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8} align="center">
          <Spinner size="xl" color="brand.500" />
          <Text>Girişler yükleniyor...</Text>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading
              size="2xl"
              bgGradient="linear(to-r, brand.500, purple.500)"
              bgClip="text"
            >
              Zihin Aynası
            </Heading>
            <Text fontSize="lg" color="gray.600">
              Düşüncelerinizi kaydedin, analiz edin ve gelişin
            </Text>
          </VStack>

          <Button
            leftIcon={<ExternalLinkIcon />}
            colorScheme="red"
            variant="solid"
            onClick={handleLogout}
            aria-label="Çıkış yap"
          >
            Çıkış Yap
          </Button>
        </HStack>

        {/* Navigation Cards */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <Card
            bg={cardBg}
            borderRadius="xl"
            boxShadow="lg"
            border="1px"
            borderColor={borderColor}
            cursor="pointer"
            _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
            transition="all 0.2s"
            onClick={() => navigate("/new-entry")}
          >
            <CardBody textAlign="center">
              <AddIcon boxSize={8} color="brand.500" mb={4} />
              <Heading size="md" mb={2}>Yeni Giriş</Heading>
              <Text color="gray.600">Bugünkü düşüncelerinizi kaydedin</Text>
            </CardBody>
          </Card>

          <Card
            bg={cardBg}
            borderRadius="xl"
            boxShadow="lg"
            border="1px"
            borderColor={borderColor}
            cursor="pointer"
            _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
            transition="all 0.2s"
            onClick={() => navigate("/archive")}
          >
            <CardBody textAlign="center">
              <CalendarIcon boxSize={8} color="purple.500" mb={4} />
              <Heading size="md" mb={2}>Arşiv</Heading>
              <Text color="gray.600">Geçmiş girişlerinizi görüntüleyin</Text>
            </CardBody>
          </Card>

          <Card
            bg={cardBg}
            borderRadius="xl"
            boxShadow="lg"
            border="1px"
            borderColor={borderColor}
            cursor="pointer"
            _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
            transition="all 0.2s"
            onClick={() => navigate("/stats")}
          >
            <CardBody textAlign="center">
              <ViewIcon boxSize={8} color="green.500" mb={4} />
              <Heading size="md" mb={2}>İstatistikler</Heading>
              <Text color="gray.600">Yazma alışkanlıklarınızı analiz edin</Text>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Recent Entries */}
        <Box>
          <HStack justify="space-between" align="center" mb={6}>
            <Heading size="lg">Son Girişler</Heading>
            <Button
              variant="ghost"
              colorScheme="brand"
              onClick={() => navigate("/archive")}
            >
              Tümünü Gör
            </Button>
          </HStack>

          {error && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}

          {entries.length === 0 ? (
            <Card bg={cardBg} borderRadius="xl" boxShadow="lg">
              <CardBody textAlign="center" py={12}>
                <TimeIcon boxSize={12} color="gray.400" mb={4} />
                <Heading size="md" color="gray.500" mb={2}>
                  Henüz giriş yok
                </Heading>
                <Text color="gray.600" mb={6}>
                  İlk günlük girişinizi oluşturmak için "Yeni Giriş" butonuna tıklayın
                </Text>
                <Button
                  colorScheme="brand"
                  size="lg"
                  onClick={() => navigate("/new-entry")}
                >
                  İlk Girişi Oluştur
                </Button>
              </CardBody>
            </Card>
          ) : (
            <VStack spacing={4} align="stretch">
              {entries.map((entry) => (
                <Card
                  key={entry.id}
                  bg={cardBg}
                  borderRadius="xl"
                  boxShadow="lg"
                  border="1px"
                  borderColor={borderColor}
                  // tıklama kaldırıldı
                  transition="all 0.2s"
                >
                  <CardHeader pb={2}>
                    <HStack justify="space-between" align="center">
                      <Badge colorScheme="brand" variant="subtle">
                        {formatDate(entry.created_at)}
                      </Badge>
                      {entry.mood_score && moodIcons[entry.mood_score] && (
                        <Box color={moodIcons[entry.mood_score].color} fontSize="2xl" title={moodIcons[entry.mood_score].label}>
                          {moodIcons[entry.mood_score].icon}
                        </Box>
                      )}
                    </HStack>
                  </CardHeader>
                  <CardBody pt={0}>
                    <Text
                      noOfLines={3}
                      color="gray.700"
                      fontSize="md"
                      lineHeight="tall"
                    >
                      {entry.text}
                    </Text>
                  </CardBody>
                </Card>
              ))}
            </VStack>
          )}
        </Box>
      </VStack>
    </Container>
  );
} 
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Textarea,
  Button,
  Alert,
  AlertIcon,
  useColorModeValue,
  HStack,
  IconButton,
} from "@chakra-ui/react";
import { ArrowBackIcon } from "@chakra-ui/icons";
import { useAuth } from "../hooks/useAuth.jsx";
import { FaRegSadTear, FaRegMeh, FaRegSmile, FaSmileBeam, FaRegFrown } from "react-icons/fa";

export default function NewEntry() {
  const [content, setContent] = useState("");
  const [mood, setMood] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [analysis, setAnalysis] = useState("");

  const { logout } = useAuth();
  const navigate = useNavigate();

  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const moodOptions = [
    { value: 1, icon: <FaRegFrown />, label: "Çok üzgün", color: "blue.400" },
    { value: 2, icon: <FaRegSadTear />, label: "Üzgün", color: "cyan.400" },
    { value: 3, icon: <FaRegMeh />, label: "Nötr", color: "gray.400" },
    { value: 4, icon: <FaRegSmile />, label: "Mutlu", color: "green.400" },
    { value: 5, icon: <FaSmileBeam />, label: "Çok mutlu", color: "yellow.400" },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!mood) {
      setError("Lütfen bir duygu durumu seçin");
      return;
    }
    if (!content.trim()) {
      setError("Lütfen bir günlük girişi yazın");
      return;
    }
    setError("");
    setSuccess("");
    setAnalysis("");
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      // 1. Girişi kaydet
      const res = await fetch("http://localhost:8000/entries", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ text: content.trim(), mood_score: mood }),
      });
      if (res.status === 401) {
        logout();
        navigate("/login");
        return;
      }
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Giriş oluşturulamadı");
      }
      setSuccess("Günlük girişi başarıyla kaydedildi!");
      // 2. Analiz API'sine istek at
      const analyzeRes = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: content.trim() }),
      });
      if (analyzeRes.ok) {
        const analyzeData = await analyzeRes.json();
        setAnalysis(analyzeData);
      } else {
        setAnalysis("Analiz alınamadı.");
      }
      setContent("");
      setMood(null);
      // navigate işlemini kaldırıyoruz, analiz gösterilecek
    } catch (err) {
      setError(err.message || "Bir hata oluştu");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between" align="center">
          <IconButton
            icon={<ArrowBackIcon />}
            onClick={() => navigate("/")}
            variant="ghost"
            aria-label="Geri dön"
          />
          <Heading size="lg" textAlign="center" flex={1}>
            Yeni Günlük Girişi
          </Heading>
          <Box w={10} /> {/* Spacer for centering */}
        </HStack>

        <Box
          p={6}
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

          {/* Analiz sonucu gösterimi */}
          {analysis?.distortions?.length > 0 && (
            <Box
              border="1px solid"
              borderColor="gray.300"
              borderRadius="md"
              p={4}
              mb={4}
              bg="gray.50"
            >
              <Heading size="sm" mb={3}>AI Analizi – Bilişsel Çarpıtmalar</Heading>
              <VStack spacing={4} align="stretch">
                {analysis.distortions.map((d, i) => (
                  <Box
                    key={i}
                    p={3}
                    border="1px solid"
                    borderColor="gray.200"
                    borderRadius="md"
                    bg="white"
                  >
                    <Text fontSize="sm"><strong>Tür:</strong> {d.type}</Text>
                    <Text fontSize="sm"><strong>İfade:</strong> {d.sentence}</Text>
                    <Text fontSize="sm"><strong>Açıklama:</strong> {d.explanation}</Text>
                    <Text fontSize="sm"><strong>Alternatif:</strong> {d.alternative}</Text>
                  </Box>
                ))}
              </VStack>
            </Box>
          )}


          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Duygu Durumu</FormLabel>
                <HStack spacing={3} justify="center">
                  {moodOptions.map((opt) => (
                    <Button
                      key={opt.value}
                      type="button"
                      onClick={() => setMood(opt.value)}
                      variant={mood === opt.value ? "solid" : "ghost"}
                      colorScheme={mood === opt.value ? "yellow" : "gray"}
                      size="lg"
                      fontSize="2xl"
                      borderWidth={mood === opt.value ? 2 : 1}
                      borderColor={mood === opt.value ? opt.color : "gray.200"}
                      boxShadow={mood === opt.value ? "md" : "none"}
                      aria-label={opt.label}
                    >
                      {opt.icon}
                    </Button>
                  ))}
                </HStack>
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Bugün neler yaşadınız?</FormLabel>
                <Textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Düşüncelerinizi, duygularınızı, yaşadıklarınızı buraya yazın..."
                  size="lg"
                  minH="300px"
                  resize="vertical"
                  disabled={isLoading}
                />
              </FormControl>

              <Button
                type="submit"
                colorScheme="brand"
                size="lg"
                w="full"
                isLoading={isLoading}
                loadingText="Kaydediliyor..."
              >
                Kaydet
              </Button>
            </VStack>
          </form>
        </Box>
      </VStack>
    </Container>
  );
} 
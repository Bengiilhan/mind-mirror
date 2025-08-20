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
  Badge,
  Progress,
  Divider,
} from "@chakra-ui/react";
import { ArrowBackIcon, WarningIcon, InfoIcon } from "@chakra-ui/icons";
import { useAuth } from "../hooks/useAuth.jsx";
import { FaRegSadTear, FaRegMeh, FaRegSmile, FaSmileBeam, FaRegFrown } from "react-icons/fa";

export default function NewEntry() {
  const [content, setContent] = useState("");
  const [mood, setMood] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [analysis, setAnalysis] = useState("");
  const [savedEntry, setSavedEntry] = useState(null);

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

  // Risk seviyesi renkleri
  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'yüksek':
        return 'red';
      case 'orta':
        return 'orange';
      case 'düşük':
        return 'green';
      default:
        return 'gray';
    }
  };

  // Risk seviyesi ikonu
  const getRiskIcon = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'yüksek':
        return <WarningIcon color="red.500" />;
      case 'orta':
        return <InfoIcon color="orange.500" />;
      case 'düşük':
        return <InfoIcon color="green.500" />;
      default:
        return <InfoIcon color="gray.500" />;
    }
  };

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
    setSavedEntry(null);
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      
      // 1. ÖNCE ANALİZ YAP
      console.log("🔍 Analiz başlatılıyor...");
      
      const analyzeRes = await fetch("http://localhost:8000/analyze/", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          text: content.trim(),
          user_id: "temp" // Geçici ID
        }),
      });
      
      if (analyzeRes.ok) {
        const analyzeData = await analyzeRes.json();
        setAnalysis(analyzeData);
        console.log("✅ Analiz başarılı:", analyzeData);
        
        // 2. ANALİZ BAŞARILIYSA GÜNLÜK KAYDET
        const res = await fetch("http://localhost:8000/entries/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify({ 
            text: content.trim(), 
            mood_score: mood,
            analysis: analyzeData // Analiz sonucunu da gönder
          }),
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
        
        const savedData = await res.json();
        setSavedEntry(savedData);
        setSuccess("Günlük girişi başarıyla kaydedildi ve analiz edildi!");
        
      } else {
        console.error("❌ Analiz hatası:", analyzeRes.status);
        let errorData;
        try {
          errorData = await analyzeRes.json();
        } catch (jsonError) {
          const errorText = await analyzeRes.text();
          errorData = { detail: errorText };
        }
        
        setAnalysis({
          error: "Analiz alınamadı",
          details: errorData.detail || "Bilinmeyen hata"
        });
        
        // Analiz başarısızsa sadece günlük kaydet
        const res = await fetch("http://localhost:8000/entries/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify({ text: content.trim(), mood_score: mood }),
        });
        
        if (res.ok) {
          const savedData = await res.json();
          setSavedEntry(savedData);
          setSuccess("Günlük girişi kaydedildi (analiz başarısız)");
        }
      }
      
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

          {/* Analiz sonucu ve kaydedilen giriş gösterimi */}
          {(analysis?.distortions?.length > 0 || savedEntry || analysis?.error) && (
            <Box
              border="1px solid"
              borderColor="gray.300"
              borderRadius="md"
              p={4}
              mb={4}
              bg="gray.50"
            >
              {/* AI Analizi */}
              {analysis?.distortions?.length > 0 && (
                <Box mb={6}>
                  <Heading size="sm" mb={3}>🧠 AI Analizi – Bilişsel Çarpıtmalar</Heading>
                  
                  {/* Risk Seviyesi Göstergesi */}
                  {analysis.risk_level && (
                    <Box mb={4} p={3} bg="white" borderRadius="md" border="1px" borderColor="gray.200">
                      <HStack spacing={2} mb={2}>
                        {getRiskIcon(analysis.risk_level)}
                        <Text fontSize="sm" fontWeight="bold">Risk Seviyesi:</Text>
                        <Badge colorScheme={getRiskColor(analysis.risk_level)} variant="subtle">
                          {analysis.risk_level.toUpperCase()}
                        </Badge>
                      </HStack>
                      <Progress 
                        value={analysis.risk_level === 'yüksek' ? 100 : analysis.risk_level === 'orta' ? 60 : 20} 
                        colorScheme={getRiskColor(analysis.risk_level)}
                        size="sm"
                      />
                    </Box>
                  )}

                  {/* Bilişsel Çarpıtmalar */}
                  <VStack spacing={4} align="stretch">
                    {analysis.distortions.map((d, i) => (
                      <Box
                        key={i}
                        p={4}
                        border="1px solid"
                        borderColor="gray.200"
                        borderRadius="md"
                        bg="white"
                        boxShadow="sm"
                      >
                        <HStack spacing={3} mb={2}>
                          <Badge colorScheme="purple" variant="subtle">
                            {d.type}
                          </Badge>
                          {d.severity && (
                            <Badge colorScheme="orange" variant="subtle">
                              {d.severity}
                            </Badge>
                          )}
                          {d.confidence && (
                            <Badge colorScheme="blue" variant="subtle">
                              %{Math.round(d.confidence * 100)}
                            </Badge>
                          )}
                        </HStack>
                        <Text fontSize="sm" mb={2}>
                          <strong>İfade:</strong> {d.sentence}
                        </Text>
                        <Text fontSize="sm" mb={2}>
                          <strong>Açıklama:</strong> {d.explanation}
                        </Text>
                        <Text fontSize="sm" color="green.600">
                          <strong>Alternatif:</strong> {d.alternative}
                        </Text>
                      </Box>
                    ))}
                  </VStack>

                  {/* Genel Öneriler */}
                  {analysis.recommendations && analysis.recommendations.length > 0 && (
                    <Box mt={4} p={3} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                      <Heading size="xs" mb={2} color="blue.700">💡 Genel Öneriler</Heading>
                      <VStack spacing={2} align="stretch">
                        {analysis.recommendations.map((rec, i) => (
                          <Text key={i} fontSize="sm" color="blue.700">
                            • {rec}
                          </Text>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  {/* Analiz Zamanı */}
                  {analysis.analysis_timestamp && (
                    <Box mt={3} textAlign="right">
                      <Text fontSize="xs" color="gray.500">
                        Analiz zamanı: {new Date(analysis.analysis_timestamp).toLocaleString('tr-TR')}
                      </Text>
                    </Box>
                  )}
                </Box>
              )}

              {/* Hata Durumu */}
              {analysis?.error && (
                <Box mb={4} p={3} bg="red.50" borderRadius="md" border="1px" borderColor="red.200">
                  <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    <Text fontSize="sm">
                      <strong>Analiz Hatası:</strong> {analysis.error}
                      {analysis.details && ` - ${analysis.details}`}
                    </Text>
                  </Alert>
                </Box>
              )}

              <Divider my={4} />
              
              {/* Kaydedilen Giriş */}
              {savedEntry && (
                <Box>
                  <Heading size="sm" mb={3}>📝 Kaydedilen Giriş</Heading>
                  <Box
                    p={4}
                    border="1px solid"
                    borderColor="gray.200"
                    borderRadius="md"
                    bg="white"
                  >
                    <HStack spacing={3} mb={3}>
                      <Badge colorScheme="green" variant="subtle">
                        {new Date(savedEntry.created_at).toLocaleString('tr-TR')}
                      </Badge>
                      {moodOptions.find(opt => opt.value === savedEntry.mood_score) && (
                        <Box 
                          color={moodOptions.find(opt => opt.value === savedEntry.mood_score).color} 
                          fontSize="lg"
                        >
                          {moodOptions.find(opt => opt.value === savedEntry.mood_score).icon}
                        </Box>
                      )}
                      <Text fontSize="sm" color="gray.600">
                        {moodOptions.find(opt => opt.value === savedEntry.mood_score)?.label}
                      </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.700">
                      {savedEntry.text}
                    </Text>
                  </Box>
                </Box>
              )}
            </Box>
          )}

          <form onSubmit={handleSubmit}>
            <VStack spacing={6} align="stretch">
              {/* Mood Selection */}
              <Box>
                <FormLabel fontSize="sm" fontWeight="bold" mb={3}>
                  Bugün nasıl hissediyorsun?
                </FormLabel>
                <HStack spacing={3} justify="center">
                  {moodOptions.map((option) => (
                    <VStack
                      key={option.value}
                      spacing={2}
                      cursor="pointer"
                      onClick={() => setMood(option.value)}
                      opacity={mood === option.value ? 1 : 0.6}
                      transition="all 0.2s"
                      _hover={{ opacity: 1, transform: "scale(1.05)" }}
                    >
                      <Box
                        p={3}
                        borderRadius="full"
                        bg={mood === option.value ? option.color : "gray.100"}
                        color={mood === option.value ? "white" : option.color}
                        fontSize="xl"
                        transition="all 0.2s"
                        _hover={{ transform: "scale(1.1)" }}
                      >
                        {option.icon}
                      </Box>
                      <Text fontSize="xs" textAlign="center" fontWeight="medium">
                        {option.label}
                      </Text>
                    </VStack>
                  ))}
                </HStack>
              </Box>

              {/* Content Input */}
              <FormControl>
                <FormLabel fontSize="sm" fontWeight="bold">
                  Günlük yazını
                </FormLabel>
                <Textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Bugün neler yaşadın? Nasıl hissettin? Düşüncelerin neler?"
                  size="lg"
                  minH="200px"
                  resize="vertical"
                  isDisabled={isLoading}
                />
              </FormControl>

              {/* Submit Button */}
              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                isLoading={isLoading}
                loadingText="Analiz ediliyor..."
                isDisabled={!content.trim() || !mood}
              >
                Kaydet ve Analiz Et
              </Button>
            </VStack>
          </form>
        </Box>
      </VStack>
    </Container>
  );
} 
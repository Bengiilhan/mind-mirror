import { useState, useEffect } from "react";
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
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Flex,
  Textarea,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  ModalFooter,
  Progress,
  Divider,
} from "@chakra-ui/react";
import { 
  ArrowBackIcon, 
  SearchIcon, 
  TimeIcon,
  EditIcon,
  DeleteIcon,
  WarningIcon,
  InfoIcon,
} from "@chakra-ui/icons";
import { useAuth } from "../hooks/useAuth.jsx";
import { FaRegSadTear, FaRegMeh, FaRegSmile, FaSmileBeam, FaRegFrown } from "react-icons/fa";

export default function Archive() {
  const [entries, setEntries] = useState([]);
  const [filteredEntries, setFilteredEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [sortBy, setSortBy] = useState("newest");
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const { logout } = useAuth();
  const navigate = useNavigate();
  
  const bg = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const moodIcons = {
    1: { icon: <FaRegFrown />, color: "blue.400", label: "Çok üzgün" },
    2: { icon: <FaRegSadTear />, color: "cyan.400", label: "Üzgün" },
    3: { icon: <FaRegMeh />, color: "gray.400", label: "Nötr" },
    4: { icon: <FaRegSmile />, color: "green.400", label: "Mutlu" },
    5: { icon: <FaSmileBeam />, color: "yellow.400", label: "Çok mutlu" },
  };

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

  useEffect(() => {
    fetchEntries();
  }, []);

  useEffect(() => {
    filterAndSortEntries();
  }, [entries, searchTerm, sortBy]);

  const fetchEntries = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/entries/", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
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
      setEntries(data);
      setIsLoading(false);
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  const filterAndSortEntries = () => {
    let filtered = entries.filter(entry =>
      entry.text.toLowerCase().includes(searchTerm.toLowerCase())
    );

    switch (sortBy) {
      case "newest":
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
      case "oldest":
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      case "mood-high":
        filtered.sort((a, b) => b.mood_score - a.mood_score);
        break;
      case "mood-low":
        filtered.sort((a, b) => a.mood_score - b.mood_score);
        break;
      default:
        break;
    }

    setFilteredEntries(filtered);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleEntryClick = (entry) => {
    setSelectedEntry(entry);
    onOpen();
  };

  const handleDeleteEntry = async (entryId) => {
    if (!window.confirm("Bu girişi silmek istediğinizden emin misiniz?")) {
      return;
    }

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:8000/entries/${entryId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (res.status === 401) {
        logout();
        navigate("/login");
        return;
      }

      if (res.ok) {
        setEntries(entries.filter(entry => entry.id !== entryId));
      } else {
        throw new Error("Giriş silinemedi");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  if (isLoading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Box textAlign="center" py={8}>
          <Spinner size="xl" />
          <Text mt={4}>Girişler yükleniyor...</Text>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <IconButton
            icon={<ArrowBackIcon />}
            onClick={() => navigate("/")}
            variant="ghost"
            aria-label="Geri dön"
          />
          <Heading size="lg" textAlign="center" flex={1}>
            Günlük Arşivi
          </Heading>
          <Box w={10} />
        </HStack>

        {/* Search and Filter */}
        <HStack spacing={4}>
          <InputGroup>
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Girişlerde ara..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
          <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="newest">En Yeni</option>
            <option value="oldest">En Eski</option>
            <option value="mood-high">Mood: Yüksek → Düşük</option>
            <option value="mood-low">Mood: Düşük → Yüksek</option>
          </Select>
        </HStack>

        {/* Error Display */}
        {error && (
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {/* Entries List */}
        {filteredEntries.length === 0 ? (
          <Box textAlign="center" py={8}>
            <Text color="gray.500">
              {searchTerm ? "Arama sonucu bulunamadı" : "Henüz günlük girişi yapılmamış"}
            </Text>
          </Box>
        ) : (
          <VStack spacing={4} align="stretch">
            {filteredEntries.map((entry) => (
              <Card key={entry.id} cursor="pointer" onClick={() => handleEntryClick(entry)}>
                <CardBody>
                  <HStack justify="space-between" align="start" mb={3}>
                    <VStack align="start" spacing={1}>
                      <HStack spacing={2}>
                        <Box color={moodIcons[entry.mood_score]?.color} fontSize="lg">
                          {moodIcons[entry.mood_score]?.icon}
                        </Box>
                        <Text fontSize="sm" color="gray.600">
                          {moodIcons[entry.mood_score]?.label}
                        </Text>
                      </HStack>
                      <HStack spacing={2}>
                        <TimeIcon color="gray.400" />
                        <Text fontSize="xs" color="gray.500">
                          {formatDate(entry.created_at)}
                        </Text>
                      </HStack>
                    </VStack>
                    
                    {/* Risk Seviyesi Badge */}
                    {entry.analysis?.risk_level && (
                      <Badge 
                        colorScheme={getRiskColor(entry.analysis.risk_level)} 
                        variant="subtle"
                        size="sm"
                      >
                        {entry.analysis.risk_level.toUpperCase()}
                      </Badge>
                    )}
                  </HStack>

                  <Text noOfLines={3} color="gray.700">
                    {entry.text}
                  </Text>

                  {/* Çarpıtma Özeti */}
                  {entry.analysis?.distortions && entry.analysis.distortions.length > 0 && (
                    <Box mt={3} p={2} bg="purple.50" borderRadius="md">
                      <HStack spacing={2} mb={2}>
                        <Text fontSize="xs" fontWeight="bold" color="purple.700">
                          🧠 Tespit Edilen Çarpıtmalar:
                        </Text>
                        <Badge colorScheme="purple" variant="subtle" size="sm">
                          {entry.analysis.distortions.length}
                        </Badge>
                      </HStack>
                      <HStack spacing={2} wrap="wrap">
                        {entry.analysis.distortions.slice(0, 3).map((d, i) => (
                          <Badge key={i} colorScheme="purple" variant="outline" size="sm">
                            {d.type}
                          </Badge>
                        ))}
                        {entry.analysis.distortions.length > 3 && (
                          <Badge colorScheme="gray" variant="outline" size="sm">
                            +{entry.analysis.distortions.length - 3}
                          </Badge>
                        )}
                      </HStack>
                    </Box>
                  )}

                  {/* Hızlı Aksiyonlar */}
                  <HStack spacing={2} mt={3} justify="end">
                    <IconButton
                      icon={<EditIcon />}
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Edit functionality
                      }}
                      aria-label="Düzenle"
                    />
                    <IconButton
                      icon={<DeleteIcon />}
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteEntry(entry.id);
                      }}
                      aria-label="Sil"
                    />
                  </HStack>
                </CardBody>
              </Card>
            ))}
          </VStack>
        )}
      </VStack>

      {/* Entry Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack spacing={3}>
              <Box color={moodIcons[selectedEntry?.mood_score]?.color} fontSize="lg">
                {selectedEntry && moodIcons[selectedEntry.mood_score]?.icon}
              </Box>
              <Text>Günlük Girişi</Text>
              {selectedEntry?.analysis?.risk_level && (
                <Badge 
                  colorScheme={getRiskColor(selectedEntry.analysis.risk_level)} 
                  variant="subtle"
                >
                  {selectedEntry.analysis.risk_level.toUpperCase()}
                </Badge>
              )}
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {selectedEntry && (
              <VStack spacing={4} align="stretch">
                {/* Tarih ve Mood */}
                <Box>
                  <Text fontSize="sm" color="gray.500" mb={2}>
                    {formatDate(selectedEntry.created_at)}
                  </Text>
                  <HStack spacing={2}>
                    <Box color={moodIcons[selectedEntry.mood_score]?.color} fontSize="lg">
                      {moodIcons[selectedEntry.mood_score]?.icon}
                    </Box>
                    <Text fontWeight="bold">
                      {moodIcons[selectedEntry.mood_score]?.label}
                    </Text>
                  </HStack>
                </Box>

                {/* Giriş Metni */}
                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={2}>Günlük Yazısı:</Text>
                  <Textarea
                    value={selectedEntry.text}
                    isReadOnly
                    minH="100px"
                    resize="none"
                  />
                </Box>

                {/* AI Analizi */}
                {selectedEntry.analysis && (
                  <Box>
                    <Heading size="sm" mb={3}>🧠 AI Analizi</Heading>
                    
                    {/* Risk Seviyesi */}
                    {selectedEntry.analysis.risk_level && (
                      <Box mb={4} p={3} bg="gray.50" borderRadius="md">
                        <HStack spacing={2} mb={2}>
                          {getRiskIcon(selectedEntry.analysis.risk_level)}
                          <Text fontSize="sm" fontWeight="bold">Risk Seviyesi:</Text>
                          <Badge colorScheme={getRiskColor(selectedEntry.analysis.risk_level)} variant="subtle">
                            {selectedEntry.analysis.risk_level.toUpperCase()}
                          </Badge>
                        </HStack>
                        <Progress 
                          value={selectedEntry.analysis.risk_level === 'yüksek' ? 100 : 
                                 selectedEntry.analysis.risk_level === 'orta' ? 60 : 20} 
                          colorScheme={getRiskColor(selectedEntry.analysis.risk_level)}
                          size="sm"
                        />
                      </Box>
                    )}

                    {/* Çarpıtmalar */}
                    {selectedEntry.analysis.distortions && selectedEntry.analysis.distortions.length > 0 && (
                      <Box mb={4}>
                        <Text fontSize="sm" fontWeight="bold" mb={2}>Bilişsel Çarpıtmalar:</Text>
                        <VStack spacing={3} align="stretch">
                          {selectedEntry.analysis.distortions.map((d, i) => (
                            <Box
                              key={i}
                              p={3}
                              border="1px solid"
                              borderColor="gray.200"
                              borderRadius="md"
                              bg="white"
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
                      </Box>
                    )}

                    {/* Öneriler */}
                    {selectedEntry.analysis.recommendations && selectedEntry.analysis.recommendations.length > 0 && (
                      <Box>
                        <Text fontSize="sm" fontWeight="bold" mb={2}>💡 Öneriler:</Text>
                        <VStack spacing={2} align="stretch">
                          {selectedEntry.analysis.recommendations.map((rec, i) => (
                            <Text key={i} fontSize="sm" color="blue.700">
                              • {rec}
                            </Text>
                          ))}
                        </VStack>
                      </Box>
                    )}

                    {/* Analiz Zamanı */}
                    {selectedEntry.analysis.analysis_timestamp && (
                      <Box mt={3} textAlign="right">
                        <Text fontSize="xs" color="gray.500">
                          Analiz zamanı: {new Date(selectedEntry.analysis.analysis_timestamp).toLocaleString('tr-TR')}
                        </Text>
                      </Box>
                    )}
                  </Box>
                )}
              </VStack>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Container>
  );
}
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
} from "@chakra-ui/react";
import { 
  ArrowBackIcon, 
  SearchIcon, 
  TimeIcon,
  EditIcon,
  DeleteIcon
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

  useEffect(() => {
    fetchEntries();
  }, []);

  useEffect(() => {
    filterAndSortEntries();
  }, [entries, searchTerm, sortBy]);

  const fetchEntries = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/entries", {
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
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const filterAndSortEntries = () => {
    let filtered = entries;

    // Arama filtresi
    if (searchTerm) {
      filtered = filtered.filter(entry =>
        entry.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Sıralama
    filtered.sort((a, b) => {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);
      
      if (sortBy === "newest") {
        return dateB - dateA;
      } else {
        return dateA - dateB;
      }
    });

    setFilteredEntries(filtered);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    // UTC'yi local'e çevir
    return date.toLocaleString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
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

      if (!res.ok) {
        throw new Error("Giriş silinemedi");
      }

      // Listeyi güncelle
      setEntries(entries.filter(entry => entry.id !== entryId));
    } catch (err) {
      setError(err.message);
    }
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
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <HStack spacing={4}>
            <IconButton
              icon={<ArrowBackIcon />}
              onClick={() => navigate("/")}
              variant="ghost"
              aria-label="Geri dön"
            />
            <VStack align="start" spacing={1}>
              <Heading size="xl">Arşiv</Heading>
              <Text color="gray.600">
                {entries.length} giriş bulundu
              </Text>
            </VStack>
          </HStack>
          
          <Button
            colorScheme="brand"
            onClick={() => navigate("/new-entry")}
            leftIcon={<TimeIcon />}
          >
            Yeni Giriş
          </Button>
        </HStack>

        {/* Search and Filter */}
        <HStack spacing={4}>
          <InputGroup>
            <InputLeftElement>
              <SearchIcon color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Girişlerde ara..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
          
          <Select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            w="200px"
          >
            <option value="newest">En Yeni</option>
            <option value="oldest">En Eski</option>
          </Select>
        </HStack>

        {error && (
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {/* Entries List */}
        {filteredEntries.length === 0 ? (
          <Card bg={cardBg} borderRadius="xl" boxShadow="lg">
            <CardBody textAlign="center" py={12}>
              <TimeIcon boxSize={12} color="gray.400" mb={4} />
              <Heading size="md" color="gray.500" mb={2}>
                {searchTerm ? "Arama sonucu bulunamadı" : "Henüz giriş yok"}
              </Heading>
              <Text color="gray.600" mb={6}>
                {searchTerm 
                  ? "Farklı kelimelerle aramayı deneyin"
                  : "İlk günlük girişinizi oluşturmak için 'Yeni Giriş' butonuna tıklayın"
                }
              </Text>
              {!searchTerm && (
                <Button 
                  colorScheme="brand" 
                  size="lg"
                  onClick={() => navigate("/new-entry")}
                >
                  İlk Girişi Oluştur
                </Button>
              )}
            </CardBody>
          </Card>
        ) : (
          <VStack spacing={4} align="stretch">
            {filteredEntries.map((entry) => (
              <Card 
                key={entry.id} 
                bg={cardBg} 
                borderRadius="xl" 
                boxShadow="lg"
                border="1px"
                borderColor={borderColor}
                cursor="pointer"
                _hover={{ transform: 'translateY(-1px)', boxShadow: 'xl' }}
                transition="all 0.2s"
                onClick={() => handleEntryClick(entry)}
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
                    <HStack spacing={2}>
                      <IconButton
                        icon={<EditIcon />}
                        size="sm"
                        variant="ghost"
                        colorScheme="blue"
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Edit functionality
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
      </VStack>

      {/* Entry Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {selectedEntry && (
              <HStack spacing={3}>
                {formatDate(selectedEntry.created_at)}
                {selectedEntry.mood_score && moodIcons[selectedEntry.mood_score] && (
                  <Box color={moodIcons[selectedEntry.mood_score].color} fontSize="2xl" title={moodIcons[selectedEntry.mood_score].label}>
                    {moodIcons[selectedEntry.mood_score].icon}
                  </Box>
                )}
              </HStack>
            )}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
  {selectedEntry && (
    <>
      {/* AI Analiz Sonucu */}
      {selectedEntry.analysis?.distortions && (
        <Box mb={6}>
          <Heading size="sm" mb={3}>
            Tespit Edilen Bilişsel Çarpıtmalar
          </Heading>
          <VStack spacing={4} align="stretch">
            {selectedEntry.analysis.distortions.map((d, idx) => (
              <Box 
                key={idx}
                p={4}
                border="1px solid"
                borderColor="gray.200"
                borderRadius="md"
                bg="gray.50"
              >
                <Badge colorScheme="purple" mb={2}>{d.type}</Badge>
                <Text fontSize="sm"><strong>İfade:</strong> {d.sentence}</Text>
                <Text fontSize="sm"><strong>Açıklama:</strong> {d.explanation}</Text>
                <Text fontSize="sm"><strong>Alternatif:</strong> {d.alternative}</Text>
              </Box>
            ))}
          </VStack>
        </Box>
      )}

      {/* Günlük Metni */}
      <Textarea
        value={selectedEntry.text}
        isReadOnly
        minH="300px"
        resize="vertical"
        fontSize="md"
        lineHeight="tall"
      />
    </>
  )}
</ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={onClose}>
              Kapat
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  );
}
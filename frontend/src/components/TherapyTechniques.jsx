import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Card,
  CardBody,
  Badge,
  Spinner,
  Alert,
  AlertIcon,
  useColorModeValue,
} from '@chakra-ui/react';

export default function TherapyTechniques({ distortionType, userContext, onClose }) {
  const [techniques, setTechniques] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');


  useEffect(() => {
    if (distortionType) {
      fetchTechniques();
    }
  }, [distortionType]);

  const fetchTechniques = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/rag/techniques/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          distortion_type: distortionType,
          user_context: userContext
        }),
      });

      if (!response.ok) {
        throw new Error('Teknikler alınamadı');
      }

      const data = await response.json();
      setTechniques(data.data);
    } catch (err) {
      setError(err.message || 'Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'kolay':
        return 'green';
      case 'orta':
        return 'yellow';
      case 'zor':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getDifficultyText = (difficulty) => {
    switch (difficulty) {
      case 'kolay':
        return 'Kolay';
      case 'orta':
        return 'Orta';
      case 'zor':
        return 'Zor';
      default:
        return difficulty;
    }
  };

  if (loading) {
    return (
      <VStack spacing={4} align="stretch">
        <Box textAlign="center">
          <Spinner size="lg" color="blue.500" />
          <Text mt={4} color="gray.600">Teknikler yükleniyor...</Text>
        </Box>
      </VStack>
    );
  }

  if (error) {
    return (
      <Card>
        <CardBody>
          <VStack spacing={4}>
            <Alert status="error">
              <AlertIcon />
              {error}
            </Alert>
            <Button onClick={fetchTechniques} colorScheme="blue">
              Tekrar Dene
            </Button>
          </VStack>
        </CardBody>
      </Card>
    );
  }

  if (!techniques) {
    return null;
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <Box textAlign="center" borderBottom="1px" borderColor={borderColor} pb={6}>
        <Heading size="2xl" mb={3} color="gray.800">
          🧠 {techniques.distortion_name}
        </Heading>
        <Text fontSize="lg" color="gray.600" mb={4}>
          {techniques.distortion_description}
        </Text>
        {techniques.personalized_advice && (
          <Box
            bg="gradient-to-r from-blue.50 to-purple.50"
            border="1px"
            borderColor="blue.200"
            borderRadius="xl"
            p={4}
            mb={4}
            shadow="sm"
          >
            <Text color="blue.800" fontSize="md" fontWeight="medium">
              💡 {techniques.personalized_advice}
            </Text>
          </Box>
        )}
      </Box>

      {/* Techniques */}
      <VStack spacing={4} align="stretch">
        <Heading size="lg" textAlign="center" mb={4} color="gray.800">
          🎯 Önerilen Teknikler
        </Heading>
        
        {techniques.techniques?.map((technique, index) => (
          <Card key={index} p={6} _hover={{ shadow: 'lg', borderColor: 'blue.200' }} transition="all 0.2s" border="2px" borderColor="gray.100">
            <CardBody>
              <HStack justify="space-between" align="start" mb={3}>
                <Heading size="md" color="gray.800">
                  {technique.title}
                </Heading>
                <Badge colorScheme={getDifficultyColor(technique.difficulty)} variant="subtle">
                  {getDifficultyText(technique.difficulty)}
                </Badge>
              </HStack>
              
              <Text color="gray.600" mb={3}>
                {technique.description}
              </Text>
              
              <Box bg="gray.50" borderRadius="lg" p={4} mb={3}>
                <Heading size="sm" color="gray.800" mb={2}>Egzersiz:</Heading>
                <Text color="gray.700" fontSize="sm">
                  {technique.exercise}
                </Text>
              </Box>
              
                             <Text fontSize="sm" color="gray.500">
                 ⏱️ {technique.duration}
               </Text>
            </CardBody>
          </Card>
        ))}
      </VStack>

      {/* Next Steps */}
      {techniques.next_steps && (
        <Card p={6} bg="gradient-to-r from-purple.50 to-blue.50" border="2px" borderColor="purple.200" shadow="lg">
          <CardBody>
            <Heading size="lg" textAlign="center" mb={4} color="gray.800">
              🚀 Sonraki Adımlar
            </Heading>
            <VStack spacing={2} align="stretch">
              {techniques.next_steps.map((step, index) => (
                <HStack key={index} align="start">
                  <Text color="purple.600" mr={2} mt={1}>•</Text>
                  <Text color="gray.700" fontSize="sm">{step}</Text>
                </HStack>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}

      

      {/* Action Buttons */}
              <Box textAlign="center" mt={6}>
          <Button 
            onClick={onClose} 
            colorScheme="blue"
            size="lg"
            px={8}
            py={3}
            fontSize="lg"
            fontWeight="semibold"
            shadow="lg"
            _hover={{ shadow: 'xl' }}
            transition="all 0.2s"
          >
            ✕ Kapat
          </Button>
        </Box>
    </VStack>
  );
}

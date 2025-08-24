import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Card,
  CardBody,
  Progress,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  Alert,
  AlertIcon,
  Spinner,
  Button,
  useToast,
  Divider,
  List,
  ListItem,
  ListIcon,
  IconButton,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Tag,
  Flex
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon, InfoIcon, ArrowBackIcon, TimeIcon, StarIcon } from '@chakra-ui/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';


const Statistics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiInsightsLoading, setAiInsightsLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/statistics/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        setError('İstatistikler yüklenemedi');
      }
    } catch (err) {
      setError('Bağlantı hatası');
    } finally {
      setLoading(false);
    }
  };

  const fetchAIInsights = async () => {
    try {
      setAiInsightsLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/statistics/insights', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(prev => ({ ...prev, ai_insights: data.ai_insights }));
        toast({
          title: 'AI İçgörüleri',
          description: 'Yeni içgörüler yüklendi',
          status: 'success',
          duration: 3000,
        });
      } else {
        // HTTP hata kodları için daha detaylı hata mesajları
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'AI içgörüleri yüklenemedi';
        
        toast({
          title: 'Hata',
          description: errorMessage,
          status: 'error',
          duration: 5000,
        });
        
        // Hata durumunda fallback içgörü göster
        setStats(prev => ({ 
          ...prev, 
          ai_insights: "AI analizi şu anda kullanılamıyor. İstatistiklerinizi manuel olarak inceleyebilirsiniz." 
        }));
      }
    } catch (err) {
      console.error('AI Insights hatası:', err);
      
      toast({
        title: 'Bağlantı Hatası',
        description: 'AI içgörüleri yüklenemedi. Lütfen tekrar deneyin.',
        status: 'error',
        duration: 5000,
      });
      
      // Network hatası durumunda fallback içgörü göster
      setStats(prev => ({ 
        ...prev, 
        ai_insights: "Bağlantı hatası nedeniyle AI analizi yapılamadı. İstatistiklerinizi manuel olarak inceleyebilirsiniz." 
      }));
    } finally {
      setAiInsightsLoading(false);
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>İstatistikler yükleniyor...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  if (!stats) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>İstatistikler yükleniyor...</Text>
      </Box>
    );
  }

  // Hiç giriş yapmamışsa özel mesaj göster
  if (stats.entry_count === 0) {
    return (
      <Box p={6} maxW="1200px" mx="auto">
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
              İlerleme İstatistikleri
            </Heading>
            <Box w={10} />
          </HStack>
          
          {/* Boş durum mesajı */}
          <Card>
            <CardBody>
              <VStack spacing={4} textAlign="center" py={10}>
                <InfoIcon w={16} h={16} color="blue.500" />
                <Heading size="md" color="gray.700">
                  Henüz İstatistik Bulunmuyor
                </Heading>
                <Text color="gray.600" maxW="500px">
                  İlk günlük girişini yaptıktan sonra istatistiklerin burada görünecek. 
                  Düzenli giriş yaparak ilerlemeni takip edebilirsin.
                </Text>
                <Button 
                  colorScheme="blue" 
                  onClick={() => navigate("/")}
                  leftIcon={<ArrowBackIcon />}
                >
                  Ana Sayfaya Dön
                </Button>
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </Box>
    );
  }

  const { 
    entry_count, 
    total_distortions, 
    distortion_stats, 
    mood_analysis, 
    risk_analysis, 
    progress_insights,
    ai_insights,
    exercise_recommendations
  } = stats;

  return (
    <Box p={6} maxW="1200px" mx="auto">
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
            İlerleme İstatistikleri
          </Heading>
          <Box w={10} />
        </HStack>
        
        {/* Alt Başlık */}
        <Box textAlign="center">
          <Text color="gray.600">
            {entry_count} giriş analiz edildi • {total_distortions} çarpıtma tespit edildi
          </Text>
        </Box>

        {/* Genel İstatistikler */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <Stat>
            <StatLabel>Toplam Giriş</StatLabel>
            <StatNumber>{entry_count}</StatNumber>
            <StatHelpText>
              <StatArrow type="increase" />
              Aktif kullanım
            </StatHelpText>
          </Stat>

          <Stat>
            <StatLabel>Çarpıtma Sayısı</StatLabel>
            <StatNumber>{total_distortions}</StatNumber>
            <StatHelpText>
              Ortalama: {(total_distortions / entry_count).toFixed(1)} / giriş
            </StatHelpText>
          </Stat>

          <Stat>
            <StatLabel>Risk Seviyesi</StatLabel>
            <StatNumber>{risk_analysis?.high_risk_percentage || 0}%</StatNumber>
            <StatHelpText>
              Yüksek riskli girişler
              {risk_analysis?.medium_plus_risk_percentage && (
                <Text fontSize="xs" color="gray.500">
                  Orta+ risk: {risk_analysis.medium_plus_risk_percentage}%
                </Text>
              )}
            </StatHelpText>
          </Stat>
        </SimpleGrid>

        {/* Çarpıtma Analizi */}
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>En Yaygın Çarpıtmalar</Heading>
            <VStack spacing={3} align="stretch">
              {distortion_stats?.most_common?.map((distortion, index) => (
                <Box key={index}>
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="medium">{distortion.type}</Text>
                    <Badge colorScheme="blue">{distortion.count} kez</Badge>
                  </HStack>
                  <Progress 
                    value={distortion.percentage} 
                    colorScheme="blue" 
                    size="sm"
                  />
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    {distortion.percentage}% oranında
                  </Text>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>

        {/* Ruh Hali Trend Grafiği */}
        <Card>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Heading size="md">Ruh Hali Değişimi</Heading>
                {mood_analysis?.trend_direction && (
                  <HStack spacing={2}>
                    <Tag colorScheme={mood_analysis.trend_direction === 'iyileşiyor' ? 'green' : mood_analysis.trend_direction === 'kötüleşiyor' ? 'red' : 'gray'}>
                      {mood_analysis.trend_direction}
                    </Tag>
                    {mood_analysis.trend_percentage > 0 && (
                      <Text fontSize="sm" color="gray.600">
                        %{mood_analysis.trend_percentage} değişim
                      </Text>
                    )}
                  </HStack>
                )}
              </HStack>
              
              {mood_analysis?.mood_timeline && mood_analysis.mood_timeline.length > 0 ? (
                <Box h="300px">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mood_analysis.mood_timeline}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tick={{ fontSize: 12 }}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis 
                        domain={[1, 5]}
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => {
                          const labels = { 
                            1: 'Çok Üzgün', 
                            2: 'Üzgün', 
                            3: 'Nötr', 
                            4: 'Mutlu', 
                            5: 'Çok Mutlu'
                          };
                          return labels[value] || value;
                        }}
                      />
                      <Tooltip 
                        formatter={(value, name, props) => {
                          // props.payload.mood kullanarak doğru mood string'ini al
                          const mood = props.payload.mood;
                          return [mood, 'Ruh Hali'];
                        }}
                        labelFormatter={(label) => `Tarih: ${label}`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="mood_score" 
                        stroke="#3182ce" 
                        strokeWidth={3}
                        dot={{ fill: '#3182ce', strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6, stroke: '#3182ce', strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box textAlign="center" py={10}>
                  <Text color="gray.500">Henüz yeterli ruh hali verisi bulunmuyor.</Text>
                  <Text fontSize="sm" color="gray.400">
                    Daha fazla giriş yaptıktan sonra trend grafiği burada görünecek.
                  </Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>



        {/* Egzersiz Önerileri */}
        {exercise_recommendations && (
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Kişiselleştirilmiş Egzersizler</Heading>
              
                             <VStack spacing={6} align="stretch">
                 {/* Odak Alanları */}
                 {exercise_recommendations.focus_areas && exercise_recommendations.focus_areas.length > 0 && (
                   <Box>
                     <Text fontWeight="medium" mb={3}>Odak Alanları</Text>
                     <Flex wrap="wrap" gap={2}>
                       {exercise_recommendations.focus_areas.map((area, index) => (
                         <Tag key={index} colorScheme="blue" size="md">
                           <StarIcon mr={1} />
                           {area}
                         </Tag>
                       ))}
                     </Flex>
                   </Box>
                 )}

                 <Tabs variant="enclosed">
                   <TabList>
                     <Tab>Günlük Egzersizler</Tab>
                     <Tab>Haftalık Görevler</Tab>
                     <Tab>Acil Durum Araçları</Tab>
                   </TabList>
                   
                   <TabPanels>
                     {/* Günlük Egzersizler */}
                     <TabPanel>
                       <VStack spacing={4} align="stretch">
                         {exercise_recommendations.daily_exercises && exercise_recommendations.daily_exercises.length > 0 ? (
                           exercise_recommendations.daily_exercises.map((exercise, index) => (
                             <Card key={index} variant="outline">
                               <CardBody>
                                 <VStack align="stretch" spacing={3}>
                                   <HStack justify="space-between">
                                     <Heading size="sm">{exercise.title}</Heading>
                                     <Tag colorScheme={
                                       exercise.difficulty === 'kolay' ? 'green' : 
                                       exercise.difficulty === 'orta' ? 'yellow' : 'red'
                                     }>
                                       {exercise.difficulty}
                                     </Tag>
                                   </HStack>
                                   <Text color="gray.700">{exercise.description}</Text>
                                   <HStack>
                                     <TimeIcon color="blue.500" />
                                     <Text fontSize="sm" color="gray.600">{exercise.duration}</Text>
                                     {exercise.focus && (
                                       <Tag size="sm" colorScheme="blue">{exercise.focus}</Tag>
                                     )}
                                   </HStack>
                                 </VStack>
                               </CardBody>
                             </Card>
                           ))
                         ) : (
                           <Box textAlign="center" py={6}>
                             <Text color="gray.500">Henüz günlük egzersiz önerisi bulunmuyor.</Text>
                           </Box>
                         )}
                       </VStack>
                     </TabPanel>
                     
                     {/* Haftalık Zorluklar */}
                     <TabPanel>
                       <VStack spacing={4} align="stretch">
                         {exercise_recommendations.weekly_challenges && exercise_recommendations.weekly_challenges.length > 0 ? (
                           exercise_recommendations.weekly_challenges.map((challenge, index) => (
                             <Card key={index} variant="outline">
                               <CardBody>
                                 <VStack align="stretch" spacing={3}>
                                   <HStack justify="space-between">
                                     <Heading size="sm">{challenge.title}</Heading>
                                     <Tag colorScheme={
                                       challenge.difficulty === 'kolay' ? 'green' : 
                                       challenge.difficulty === 'orta' ? 'yellow' : 'red'
                                     }>
                                       {challenge.difficulty}
                                     </Tag>
                                   </HStack>
                                   <Text color="gray.700">{challenge.description}</Text>
                                   <HStack>
                                     <TimeIcon color="purple.500" />
                                     <Text fontSize="sm" color="gray.600">{challenge.duration}</Text>
                                   </HStack>
                                 </VStack>
                               </CardBody>
                             </Card>
                           ))
                         ) : (
                           <Box textAlign="center" py={6}>
                             <Text color="gray.500">Henüz haftalık zorluk önerisi bulunmuyor.</Text>
                           </Box>
                         )}
                       </VStack>
                     </TabPanel>
                     
                     {/* Acil Durum Araçları */}
                     <TabPanel>
                       <VStack spacing={4} align="stretch">
                         {exercise_recommendations.emergency_tools && exercise_recommendations.emergency_tools.length > 0 ? (
                           exercise_recommendations.emergency_tools.map((tool, index) => (
                             <Card key={index} variant="outline" borderColor="red.200">
                               <CardBody>
                                 <VStack align="stretch" spacing={3}>
                                   <HStack justify="space-between">
                                     <Heading size="sm" color="red.600">{tool.title}</Heading>
                                     <Tag colorScheme="red" size="sm">Acil</Tag>
                                   </HStack>
                                   <Text color="gray.700">{tool.description}</Text>
                                   <VStack align="stretch" spacing={2}>
                                     <HStack>
                                       <TimeIcon color="red.500" />
                                       <Text fontSize="sm" color="gray.600">{tool.duration}</Text>
                                     </HStack>
                                     {tool.when_to_use && (
                                       <Box bg="red.50" p={3} borderRadius="md">
                                         <Text fontSize="sm" color="red.700" fontWeight="medium">
                                           Ne zaman kullanılır: {tool.when_to_use}
                                         </Text>
                                       </Box>
                                     )}
                                   </VStack>
                                 </VStack>
                               </CardBody>
                             </Card>
                           ))
                         ) : (
                           <Box textAlign="center" py={6}>
                             <Text color="gray.500">Henüz acil durum aracı önerisi bulunmuyor.</Text>
                           </Box>
                         )}
                       </VStack>
                     </TabPanel>
                   </TabPanels>
                 </Tabs>
               </VStack>
            </CardBody>
          </Card>
        )}

        {/* İçgörüler */}
        <Card>
          <CardBody>
            <HStack justify="space-between" mb={4}>
              <Heading size="md">İçgörüler</Heading>
              <Button size="sm" colorScheme="blue" onClick={fetchAIInsights} isLoading={aiInsightsLoading}>
                AI İçgörüleri Al
              </Button>
            </HStack>
            
            <VStack spacing={4} align="stretch">
              {/* Genel Özet */}
              <Box>
                <Text fontWeight="medium" mb={2}>Genel Özet</Text>
                <Text color="gray.700">{progress_insights?.summary}</Text>
              </Box>

              {/* AI İçgörüleri */}
              {ai_insights && (
                <Box>
                  <Text fontWeight="medium" mb={2}>AI Analizi</Text>
                  <Box 
                    color="gray.700" 
                    fontSize="sm"
                    lineHeight="1.6"
                    whiteSpace="pre-line" // Satır başlarını korumak için bunu geri ekliyoruz
                    bg="gray.50"
                    p={4}
                    borderRadius="md"
                    border="1px"
                    borderColor="gray.200"
                  >
                    {ai_insights}
                  </Box>
                </Box>
              )}

              {/* Öneriler */}
              {progress_insights?.recommendations?.length > 0 && (
                <Box>
                  <Text fontWeight="medium" mb={2}>Öneriler</Text>
                  <List spacing={2}>
                    {progress_insights.recommendations.map((rec, index) => (
                      <ListItem key={index}>
                        <ListIcon as={CheckCircleIcon} color="green.500" />
                        {rec}
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>


        {/* Risk Dağılımı */}
        {risk_analysis?.risk_distribution && (
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Risk Seviyesi Dağılımı</Heading>
              <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4}>
                {Object.entries(risk_analysis.risk_distribution).map(([risk, count]) => (
                  <Box key={risk} textAlign="center">
                    <Text fontSize="2xl" fontWeight="bold" color={
                      risk === 'düşük' ? 'green.500' : 
                      risk === 'orta' ? 'orange.500' : 
                      risk === 'yüksek' ? 'red.500' : 'gray.500'
                    }>
                      {count}
                    </Text>
                    <Text fontSize="sm" textTransform="capitalize">{risk}</Text>
                    <Text fontSize="xs" color="gray.500">
                      {risk_analysis.total_entries > 0 ? Math.round((count / risk_analysis.total_entries) * 100) : 0}%
                    </Text>
                  </Box>
                ))}
              </SimpleGrid>
            </CardBody>
          </Card>
        )}

        {/* Şiddet Dağılımı */}
        {distortion_stats?.severity_distribution && (
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Çarpıtma Şiddeti</Heading>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                {Object.entries(distortion_stats.severity_distribution).map(([severity, count]) => (
                  <Box key={severity} textAlign="center">
                    <Text fontSize="2xl" fontWeight="bold" color={
                      severity === 'düşük' ? 'green.500' : 
                      severity === 'orta' ? 'yellow.500' : 'red.500'
                    }>
                      {count}
                    </Text>
                    <Text fontSize="sm" textTransform="capitalize">{severity}</Text>
                  </Box>
                ))}
              </SimpleGrid>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  );
};

export default Statistics;

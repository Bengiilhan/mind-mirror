import { useState, useEffect } from "react";
import { Box, Heading, Text, Spinner, Alert, AlertIcon, HStack, Badge } from "@chakra-ui/react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { useAuth } from "../../hooks/useAuth.jsx";

export default function MoodChart() {
  const [data, setData] = useState([]);
  const [distortionData, setDistortionData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const { logout } = useAuth();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:8000/entries/", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        logout();
        return;
      }

      if (!response.ok) {
        throw new Error("Veriler alınamadı");
      }

      const entries = await response.json();
      
      // Mood verilerini hazırla
      const moodData = entries.map(entry => ({
        date: new Date(entry.created_at).toLocaleDateString('tr-TR'),
        mood: entry.mood_score,
        timestamp: new Date(entry.created_at).getTime()
      })).sort((a, b) => a.timestamp - b.timestamp);

      // Çarpıtma verilerini hazırla
      const distortionCounts = {};
      entries.forEach(entry => {
        if (entry.analysis && entry.analysis.distortions) {
          entry.analysis.distortions.forEach(d => {
            distortionCounts[d.type] = (distortionCounts[d.type] || 0) + 1;
          });
        }
      });

      const distortionChartData = Object.entries(distortionCounts).map(([type, count]) => ({
        type,
        count
      }));

      setData(moodData);
      setDistortionData(distortionChartData);
      setIsLoading(false);
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="xl" />
        <Text mt={4}>İstatistikler yükleniyor...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Mood Chart */}
      <Box mb={8}>
        <Heading size="md" mb={4}>📊 Duygudurum Değişimi</Heading>
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#888" />
              <YAxis domain={[1, 5]} stroke="#888" />
              <Tooltip 
                contentStyle={{ background: '#fff', borderRadius: 8 }}
                formatter={(value) => [
                  value === 1 ? "Çok üzgün" : 
                  value === 2 ? "Üzgün" : 
                  value === 3 ? "Nötr" : 
                  value === 4 ? "Mutlu" : "Çok mutlu",
                  "Mood"
                ]}
              />
              <Line 
                type="monotone" 
                dataKey="mood" 
                stroke="#2563eb" 
                strokeWidth={3} 
                dot={{ r: 5 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <Text color="gray.500" textAlign="center" py={8}>
            Henüz günlük girişi yapılmamış
          </Text>
        )}
      </Box>

      {/* Distortion Chart */}
      {distortionData.length > 0 && (
        <Box mb={8}>
          <Heading size="md" mb={4}>🧠 Bilişsel Çarpıtma Analizi</Heading>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={distortionData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="type" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip 
                contentStyle={{ background: '#fff', borderRadius: 8 }}
                formatter={(value) => [value, "Tespit Edilen"]}
              />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      )}

      {/* Summary Stats */}
      <Box>
        <Heading size="md" mb={4}>📈 Özet İstatistikler</Heading>
        <HStack spacing={6} wrap="wrap">
          <Box p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
            <Text fontSize="lg" fontWeight="bold" color="blue.700">
              {data.length}
            </Text>
            <Text fontSize="sm" color="blue.600">Toplam Giriş</Text>
          </Box>
          
          {data.length > 0 && (
            <Box p={4} bg="green.50" borderRadius="md" border="1px" borderColor="green.200">
              <Text fontSize="lg" fontWeight="bold" color="green.700">
                {(data.reduce((sum, item) => sum + item.mood, 0) / data.length).toFixed(1)}
              </Text>
              <Text fontSize="sm" color="green.600">Ortalama Mood</Text>
            </Box>
          )}

          {distortionData.length > 0 && (
            <Box p={4} bg="purple.50" borderRadius="md" border="1px" borderColor="purple.200">
              <Text fontSize="lg" fontWeight="bold" color="purple.700">
                {distortionData.reduce((sum, item) => sum + item.count, 0)}
              </Text>
              <Text fontSize="sm" color="purple.600">Toplam Çarpıtma</Text>
            </Box>
          )}

          {distortionData.length > 0 && (
            <Box p={4} bg="orange.50" borderRadius="md" border="1px" borderColor="orange.200">
              <Text fontSize="lg" fontWeight="bold" color="orange.700">
                {distortionData.length}
              </Text>
              <Text fontSize="sm" color="orange.600">Çarpıtma Türü</Text>
            </Box>
          )}
        </HStack>
      </Box>
    </Box>
  );
} 
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

const API_URL = 'http://localhost:8000';

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await fetch(`${API_URL}/dashboard`, {
          headers: { Authorization: `Bearer demo-token` },
        });
        const json = await response.json();
        setDashboard(json);
      } catch (error) {
        setDashboard({
          pnl: 0,
          open_positions: 0,
          equity: 0,
          daily_drawdown: 0,
          status: 'offline',
        });
      } finally {
        setLoading(false);
      }
    };

    const interval = setInterval(load, 5000);
    load();
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <SafeAreaView style={styles.centered}>
        <ActivityIndicator size="large" />
        <Text style={styles.label}>Loading dashboard…</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.heading}>TradingBOT</Text>
        <View style={styles.card}>
          <Text style={styles.title}>Live PnL</Text>
          <Text style={styles.value}>${dashboard?.pnl ?? 0}</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Open Positions</Text>
          <Text style={styles.value}>{dashboard?.open_positions ?? 0}</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Daily Drawdown</Text>
          <Text style={styles.value}>{dashboard?.daily_drawdown ?? 0}%</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Status</Text>
          <Text style={styles.value}>{dashboard?.status ?? 'unknown'}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#071018', padding: 20 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#071018' },
  heading: { color: '#f4f6fb', fontSize: 32, fontWeight: '700', marginBottom: 18 },
  card: { backgroundColor: '#112233', borderRadius: 16, padding: 18, marginBottom: 12 },
  title: { color: '#a8bacb', fontSize: 14 },
  value: { color: '#f4f6fb', fontSize: 28, marginTop: 8, fontWeight: '700' },
  label: { color: '#f4f6fb', marginTop: 12 },
});

import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput, Button, Alert } from 'react-native';
import { useState } from 'react';

export default function App() {
  const [x, setX] = useState('0.5');
  const [t, setT] = useState('0.2');
  const [result, setResult] = useState(null);

  const predict = () => {
    // In production, call Supabase Edge Function via fetch
    const val = Math.sin(parseFloat(x)) * Math.cos(parseFloat(t));
    Alert.alert('Prediction', `Calculated u = ${val.toFixed(4)}`);
    setResult({ u: val });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>PhysicsAI Mobile Coach</Text>
      <TextInput 
        style={styles.input}
        placeholder="x" 
        value={x} 
        onChangeText={setX} 
        keyboardType="numeric" 
      />
      <TextInput 
        style={styles.input}
        placeholder="t" 
        value={t} 
        onChangeText={setT} 
        keyboardType="numeric" 
      />
      <Button title="Predict" onPress={predict} />
      {result && <Text style={styles.result}>u = {result.u.toFixed(4)}</Text>}
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, backgroundColor: '#fff' },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' },
  input: { borderBottomWidth: 1, marginBottom: 15, padding: 8 },
  result: { marginTop: 20, fontSize: 18, textAlign: 'center', color: 'blue' }
});

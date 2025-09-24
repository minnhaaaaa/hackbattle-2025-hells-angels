import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, Picker, Button } from 'react-native';
import LottieView from 'lottie-react-native';

export default function OnboardingScreen() {
  const [nickname, setNickname] = useState('');
  const [avatar, setAvatar] = useState('fox');

  return (
    <View style={styles.container}>
      <LottieView
        source={require('./assets/money-story.json')} // Replace with your Lottie file
        autoPlay
        loop
        style={styles.animation}
      />
      <Text style={styles.title}>Your money has a story…</Text>

      <Text style={styles.label}>Enter your nickname:</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g. Kethana"
        value={nickname}
        onChangeText={setNickname}
      />

      <Text style={styles.label}>Choose your avatar:</Text>
      <Picker
        selectedValue={avatar}
        style={styles.picker}
        onValueChange={(itemValue) => setAvatar(itemValue)}
      >
        <Picker.Item label="🦊 Fox" value="fox" />
        <Picker.Item label="🐼 Panda" value="panda" />
        <Picker.Item label="🐯 Tiger" value="tiger" />
      </Picker>

      <Button title="Start Your Quest" onPress={() => alert(`Welcome, ${nickname}!`)} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  animation: {
    width: 300,
    height: 300,
    alignSelf: 'center',
  },
  title: {
    fontSize: 22,
    textAlign: 'center',
    marginBottom: 20,
    fontWeight: 'bold',
  },
  label: {
    fontSize: 16,
    marginTop: 10,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    marginTop: 5,
    borderRadius: 5,
  },
  picker: {
    height: 50,
    width: '100%',
    marginTop: 5,
  },
});

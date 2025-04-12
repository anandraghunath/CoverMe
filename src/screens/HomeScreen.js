import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { Audio } from 'expo-av';

const HomeScreen = () => {
  const [isListening, setIsListening] = useState(false);
  const [currentSuggestion, setCurrentSuggestion] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [recording, setRecording] = useState(null);

  useEffect(() => {
    // Request permissions on mount
    (async () => {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        alert('Permission to access microphone was denied');
      }
    })();

    return () => {
      // Cleanup recording on unmount
      if (recording) {
        recording.stopAndUnloadAsync();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  const stopRecording = async () => {
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      // Here you would process the recorded audio
      console.log('Recording stopped and stored at', uri);
    } catch (err) {
      console.error('Failed to stop recording', err);
    }
  };

  const toggleListening = async () => {
    if (!isListening) {
      await startRecording();
      setIsListening(true);
      setCurrentSuggestion('Listening...');
    } else {
      await stopRecording();
      setIsListening(false);
      setCurrentSuggestion('');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>CoverMe</Text>
        <Text style={styles.subtitle}>Your AI Conversation Assistant</Text>
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        {/* Conversation Status */}
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>
            {isListening ? 'Active Conversation' : 'Ready to Assist'}
          </Text>
          <View style={[styles.statusIndicator, isListening && styles.activeIndicator]} />
        </View>

        {/* Current Suggestion */}
        {currentSuggestion && (
          <View style={styles.suggestionContainer}>
            <Text style={styles.suggestionText}>{currentSuggestion}</Text>
          </View>
        )}

        {/* Conversation History */}
        <View style={styles.historyContainer}>
          {conversationHistory.map((item, index) => (
            <View key={index} style={styles.historyItem}>
              <Text style={styles.historyText}>{item}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Control Button */}
      <TouchableOpacity
        style={[styles.controlButton, isListening && styles.activeButton]}
        onPress={toggleListening}
      >
        <Text style={styles.buttonText}>
          {isListening ? 'Stop Listening' : 'Start Listening'}
        </Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 16,
    color: '#888888',
    marginTop: 5,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 18,
    marginRight: 10,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#444444',
  },
  activeIndicator: {
    backgroundColor: '#00ff00',
  },
  suggestionContainer: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
  },
  suggestionText: {
    color: '#ffffff',
    fontSize: 16,
  },
  historyContainer: {
    flex: 1,
  },
  historyItem: {
    backgroundColor: '#2a2a2a',
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
  },
  historyText: {
    color: '#ffffff',
    fontSize: 14,
  },
  controlButton: {
    backgroundColor: '#333333',
    padding: 20,
    borderRadius: 10,
    margin: 20,
    alignItems: 'center',
  },
  activeButton: {
    backgroundColor: '#00ff00',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default HomeScreen; 
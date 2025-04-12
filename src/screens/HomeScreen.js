import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  Platform,
  Animated,
  Vibration,
  ScrollView,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { Audio } from 'expo-av';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');
const isSmallDevice = width < 375;

const HomeScreen = () => {
  const [isListening, setIsListening] = useState(false);
  const [currentSuggestion, setCurrentSuggestion] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [recording, setRecording] = useState(null);
  const [permissionStatus, setPermissionStatus] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  
  // Simulate conversation suggestions (in a real app, these would come from the backend)
  const demoSuggestions = [
    "Ask about their interests outside of work",
    "That's interesting! Maybe ask for more details?",
    "This might be a good time to share a similar experience",
    "Try asking how they got started with that",
    "Consider changing the topic to something lighter",
    "Great moment to compliment their perspective",
    "Ask what they think about the current trends in that area",
    "Mention how their approach is unique and thoughtful",
  ];

  useEffect(() => {
    // Fade in animation for the UI
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 800,
      useNativeDriver: true,
    }).start();
    
    // Request permissions on mount
    (async () => {
      try {
        const { status } = await Audio.requestPermissionsAsync();
        setPermissionStatus(status);
        if (status !== 'granted') {
          console.log('Permission to access microphone was denied');
          setTimeout(() => {
            Alert.alert(
              'Microphone Permission Required',
              'CoverMe needs microphone access to provide conversation suggestions.',
              [{ text: 'OK' }]
            );
          }, 1000);
        }
      } catch (err) {
        console.error('Failed to get permissions', err);
        setError('Failed to get microphone permissions');
      }
    })();

    // Simulate a connection to AirPods after 1.5 seconds
    const connectTimer = setTimeout(() => {
      setIsConnected(true);
      Vibration.vibrate(100);
    }, 1500);

    return () => {
      if (recording) {
        recording.stopAndUnloadAsync();
      }
      clearTimeout(connectTimer);
    };
  }, []);
  
  useEffect(() => {
    let interval;
    
    // Start pulse animation when listening
    if (isListening) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.15,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      ).start();
      
      // Demo: Show random suggestions every few seconds
      interval = setInterval(() => {
        const randomSuggestion = demoSuggestions[Math.floor(Math.random() * demoSuggestions.length)];
        
        // Animate the suggestion change
        Animated.sequence([
          Animated.timing(fadeAnim, {
            toValue: 0.3,
            duration: 300,
            useNativeDriver: true,
          }),
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 300,
            useNativeDriver: true,
          }),
        ]).start();
        
        setCurrentSuggestion(randomSuggestion);
        
        // Add to history after a short delay
        setTimeout(() => {
          setConversationHistory(prev => [randomSuggestion, ...prev].slice(0, 10));
        }, 1000);
      }, 5000);
    } else {
      pulseAnim.setValue(1);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isListening]);

  const startRecording = async () => {
    setError(null);
    setIsLoading(true);
    
    try {
      // Check for audio focus
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
        shouldDuckAndroid: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      Vibration.vibrate(100);
      setIsLoading(false);
    } catch (err) {
      console.error('Failed to start recording', err);
      setError('Failed to start recording. Please try again.');
      setIsLoading(false);
      
      Alert.alert(
        'Recording Error',
        'Could not start recording. Please check your microphone access and try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const stopRecording = async () => {
    setIsLoading(true);
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      console.log('Recording stopped and stored at', uri);
      Vibration.vibrate([0, 30, 30, 30]);
      setIsLoading(false);
    } catch (err) {
      console.error('Failed to stop recording', err);
      setError('Failed to stop recording. Please try again.');
      setIsLoading(false);
    }
  };

  const toggleListening = async () => {
    if (!isListening) {
      await startRecording();
      setIsListening(true);
      setCurrentSuggestion('Listening to conversation...');
    } else {
      await stopRecording();
      setIsListening(false);
      setCurrentSuggestion('');
    }
  };

  const retryPermission = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      setPermissionStatus(status);
    } catch (err) {
      console.error('Failed to get permissions', err);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="light" />
      <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <Ionicons name="headset" size={isSmallDevice ? 24 : 32} color="#4F8EF7" />
            <Text style={styles.title}>CoverMe</Text>
          </View>
          <View style={styles.connectionStatus}>
            <Text style={styles.connectionText}>
              {isConnected ? 'AirPods Connected' : 'Connecting...'}
            </Text>
            <View 
              style={[
                styles.connectionIndicator, 
                isConnected ? styles.connectionActive : styles.connectionInactive
              ]}
            />
          </View>
        </View>

        {/* Main Content */}
        <View style={styles.content}>
          {/* Current Suggestion Card */}
          <Animated.View 
            style={[
              styles.suggestionCard,
              { opacity: fadeAnim }
            ]}
          >
            {isListening ? (
              <>
                <Animated.View 
                  style={[
                    styles.listeningIndicator, 
                    {transform: [{scale: pulseAnim}]}
                  ]}
                >
                  <Ionicons name="mic" size={32} color="#fff" />
                </Animated.View>
                <Text style={styles.suggestionTitle}>
                  {currentSuggestion ? 'Suggestion:' : 'Listening...'}
                </Text>
                <Text style={styles.suggestionText}>
                  {currentSuggestion || "I'm analyzing the conversation..."}
                </Text>
              </>
            ) : (
              <>
                <View style={styles.idleIcon}>
                  <Ionicons name="ear-outline" size={48} color="#4F8EF7" />
                </View>
                <Text style={styles.suggestionTitle}>Ready When You Are</Text>
                <Text style={styles.suggestionText}>
                  Tap the button below to start listening and receive real-time conversation suggestions
                </Text>
              </>
            )}
            
            {isLoading && (
              <View style={styles.loadingOverlay}>
                <ActivityIndicator size="large" color="#4F8EF7" />
              </View>
            )}
          </Animated.View>
          
          {/* Error Message */}
          {error && (
            <View style={styles.errorContainer}>
              <Ionicons name="alert-circle-outline" size={18} color="#F44336" />
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}
          
          {/* Privacy Notice */}
          <View style={styles.privacyContainer}>
            <Ionicons name="shield-checkmark-outline" size={18} color="#888" />
            <Text style={styles.privacyText}>
              Privacy-first: No conversations stored or shared
            </Text>
          </View>

          {/* Recent Suggestions */}
          {conversationHistory.length > 0 && (
            <View style={styles.historyContainer}>
              <Text style={styles.historyTitle}>Recent Suggestions</Text>
              <ScrollView 
                style={styles.historyScroll}
                showsVerticalScrollIndicator={false}
                contentContainerStyle={styles.historyScrollContent}
              >
                {conversationHistory.map((item, index) => (
                  <Animated.View 
                    key={index} 
                    style={[
                      styles.historyItem,
                      { opacity: 1 - (index * 0.05) }
                    ]}
                    entering={Animated.FadeInDown.duration(300).delay(index * 100)}
                  >
                    <Ionicons name="chatbubble-outline" size={16} color="#4F8EF7" />
                    <Text style={styles.historyText}>{item}</Text>
                  </Animated.View>
                ))}
              </ScrollView>
            </View>
          )}
        </View>

        {/* Control Button */}
        <TouchableOpacity
          style={[
            styles.controlButton, 
            isListening && styles.activeButton,
            (permissionStatus !== 'granted' || isLoading) && styles.disabledButton
          ]}
          onPress={toggleListening}
          disabled={permissionStatus !== 'granted' || isLoading}
          activeOpacity={0.7}
        >
          {isLoading ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <>
              <Ionicons 
                name={isListening ? "stop-circle" : "mic-circle"} 
                size={32} 
                color="#fff" 
              />
              <Text style={styles.buttonText}>
                {isListening ? 'Stop Listening' : 'Start Listening'}
              </Text>
            </>
          )}
        </TouchableOpacity>
        
        {/* Permission Warning */}
        {permissionStatus !== 'granted' && (
          <TouchableOpacity 
            style={styles.permissionWarning}
            onPress={retryPermission}
          >
            <Ionicons name="warning-outline" size={18} color="#FFC107" />
            <Text style={styles.permissionText}>
              Microphone permission is required. Tap to request again.
            </Text>
          </TouchableOpacity>
        )}
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#121212',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  header: {
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginLeft: 8,
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectionText: {
    color: '#888',
    fontSize: 12,
    marginRight: 6,
  },
  connectionIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  connectionActive: {
    backgroundColor: '#4CAF50',
  },
  connectionInactive: {
    backgroundColor: '#FFC107',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  suggestionCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    minHeight: 200,
    position: 'relative',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(26, 26, 26, 0.7)',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listeningIndicator: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#4F8EF7',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  idleIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(79, 142, 247, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  suggestionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  suggestionText: {
    color: '#ddd',
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 22,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(244, 67, 54, 0.1)',
    padding: 10,
    borderRadius: 8,
    marginTop: 12,
  },
  errorText: {
    color: '#F44336',
    fontSize: 14,
    marginLeft: 8,
  },
  privacyContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
    marginBottom: 16,
  },
  privacyText: {
    color: '#888',
    fontSize: 12,
    marginLeft: 6,
  },
  historyContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginTop: 12,
  },
  historyTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  historyScroll: {
    flex: 1,
  },
  historyScrollContent: {
    paddingBottom: 8,
  },
  historyItem: {
    flexDirection: 'row',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
    alignItems: 'flex-start',
  },
  historyText: {
    color: '#ddd',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  controlButton: {
    backgroundColor: '#4F8EF7',
    flexDirection: 'row',
    borderRadius: 30,
    margin: 20,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  activeButton: {
    backgroundColor: '#F44336',
  },
  disabledButton: {
    backgroundColor: '#666666',
    opacity: 0.7,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  permissionWarning: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    backgroundColor: 'rgba(255, 193, 7, 0.1)',
    padding: 10,
    borderRadius: 8,
    marginHorizontal: 20,
  },
  permissionText: {
    color: '#FFC107',
    fontSize: 14,
    marginLeft: 6,
    flex: 1,
  },
});

export default HomeScreen; 
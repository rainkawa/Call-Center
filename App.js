import React, { useCallback, useEffect, useRef, useState } from 'react';
import { BackHandler, StyleSheet, Text, View, Pressable, Platform } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { WebView } from 'react-native-webview';
import * as ScreenOrientation from 'expo-screen-orientation';
import { NavigationBar } from 'expo-navigation-bar';
import { activateKeepAwakeAsync } from 'expo-keep-awake';
import * as Haptics from 'expo-haptics';
import * as SplashScreen from 'expo-splash-screen';

import gameHtml from './webgame/index.html';

SplashScreen.preventAutoHideAsync?.().catch(() => {});

const ACK_TIMEOUT = 350;

export default function App() {
  const webViewRef = useRef(null);
  const pendingBackRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);

  const reload = useCallback(() => {
    setError(false);
    setReady(false);
    webViewRef.current?.reload();
  }, []);

  const clearPendingBack = useCallback(() => {
    if (pendingBackRef.current) {
      clearTimeout(pendingBackRef.current);
      pendingBackRef.current = null;
    }
  }, []);

  const requestBack = useCallback(() => {
    clearPendingBack();
    webViewRef.current?.injectJavaScript(
      'window.__nativeMessage && window.__nativeMessage("back"); true;'
    );
    pendingBackRef.current = setTimeout(() => {
      pendingBackRef.current = null;
      BackHandler.exitApp();
    }, ACK_TIMEOUT);
    return true;
  }, [clearPendingBack]);

  const onHardwareBack = useCallback(() => {
    if (!ready) {
      BackHandler.exitApp();
      return true;
    }
    return requestBack();
  }, [ready, requestBack]);

  useEffect(() => {
    ScreenOrientation.lockAsync(
      ScreenOrientation.OrientationLock.LANDSCAPE
    ).catch(() => {});
    activateKeepAwakeAsync().catch(() => {});
    const sub = BackHandler.addEventListener('hardwareBackPress', onHardwareBack);
    return () => {
      sub.remove();
      clearPendingBack();
    };
  }, [onHardwareBack, clearPendingBack]);

  const onMessage = useCallback(
    (event) => {
      let data;
      try {
        data = JSON.parse(event.nativeEvent.data);
      } catch (e) {
        return;
      }
      switch (data && data.t) {
        case 'ready':
          setReady(true);
          SplashScreen.hideAsync?.().catch(() => {});
          break;
        case 'haptic':
          try {
            const style = data.style || 'selection';
            if (style === 'impact') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            else if (style === 'success' || style === 'error' || style === 'warning') {
              Haptics.notificationAsync(Haptics.NotificationFeedbackType[style === 'success' ? 'Success' : 'Error']);
            } else Haptics.selectionAsync();
          } catch (e) {}
          break;
        case 'back':
          clearPendingBack();
          if (!data.handled) BackHandler.exitApp();
          break;
        case 'toast':
          break;
        default:
          break;
      }
    },
    [clearPendingBack]
  );

  return (
    <View style={styles.container}>
      <NavigationBar hidden style="dark" />
      <StatusBar hidden style="light" />
      <WebView
        ref={webViewRef}
        source={gameHtml}
        style={styles.webview}
        originWhitelist={['*']}
        javaScriptEnabled
        domStorageEnabled
        allowFileAccess
        setSupportMultipleWindows={false}
        setBuiltInZoomControls={false}
        setDisplayZoomControls={false}
        overScrollMode="never"
        androidLayerType="hardware"
        allowsInlineMediaPlayback
        mediaPlaybackRequiresUserAction={false}
        hideKeyboardAccessoryView
        keyboardDisplayRequiresUserAction={false}
        textZoom={100}
        onMessage={onMessage}
        onError={() => setError(true)}
        onHttpError={() => setError(true)}
        onRenderProcessGone={() => setError(true)}
      />
      {error && (
        <View style={[styles.overlay, StyleSheet.absoluteFill]}>
          <Text style={styles.errorTitle}>Game failed to load</Text>
          <Text style={styles.errorText}>Something went wrong in the WebView.</Text>
          <Pressable style={styles.reloadBtn} onPress={reload}>
            <Text style={styles.reloadText}>Reload</Text>
          </Pressable>
        </View>
      )}
      {!ready && !error && (
        <View style={[styles.overlay, StyleSheet.absoluteFill]}>
          <Text style={styles.title}>CALL CENTER TYCOON 3D</Text>
          <Text style={styles.subtitle}>Loading your call floor…</Text>
          <View style={styles.spinner} />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d1117',
  },
  webview: {
    flex: 1,
    backgroundColor: '#0d1117',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0d1117',
  },
  title: {
    color: '#00e5c7',
    fontSize: 26,
    fontWeight: '800',
    letterSpacing: 2,
    fontFamily: Platform.OS === 'android' ? 'monospace' : undefined,
  },
  subtitle: {
    color: '#8b949e',
    fontSize: 14,
    marginTop: 12,
  },
  spinner: {
    marginTop: 24,
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 3,
    borderColor: '#2a3540',
    borderTopColor: '#00e5c7',
  },
  errorTitle: {
    color: '#f85149',
    fontSize: 20,
    fontWeight: '700',
  },
  errorText: {
    color: '#8b949e',
    fontSize: 14,
    marginTop: 8,
  },
  reloadBtn: {
    marginTop: 20,
    paddingHorizontal: 28,
    paddingVertical: 12,
    borderRadius: 10,
    backgroundColor: '#00e5c7',
  },
  reloadText: {
    color: '#0d1117',
    fontSize: 16,
    fontWeight: '700',
  },
});
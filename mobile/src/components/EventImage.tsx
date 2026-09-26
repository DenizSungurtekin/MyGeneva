import { Feather } from '@expo/vector-icons';
import React, { useMemo, useState } from 'react';
import { Image, StyleProp, StyleSheet, View, ViewStyle } from 'react-native';

import { useTheme } from '../theme';

interface Props {
  imageUrl: string | null | undefined;
  variant: 'event' | 'restaurant';
  style?: StyleProp<ViewStyle>;
  iconSize?: number;
}

export function EventImage({ imageUrl, variant, style, iconSize = 24 }: Props) {
  const { theme } = useTheme();
  const [failed, setFailed] = useState(false);
  const showImage = Boolean(imageUrl) && !failed;

  const bg =
    variant === 'event'
      ? theme.colors.placeholderEvent
      : theme.colors.placeholderRestaurant;
  const iconColor =
    variant === 'event'
      ? theme.colors.placeholderEventIcon
      : theme.colors.placeholderRestaurantIcon;
  const iconName = variant === 'event' ? 'image' : 'coffee';

  const containerStyle = useMemo(
    () => [styles.container, { backgroundColor: bg }, style],
    [bg, style],
  );

  return (
    <View style={containerStyle}>
      {showImage && imageUrl ? (
        <Image
          source={{ uri: imageUrl }}
          style={StyleSheet.absoluteFill}
          onError={() => setFailed(true)}
          resizeMode="cover"
          accessibilityIgnoresInvertColors
        />
      ) : (
        <Feather name={iconName} size={iconSize} color={iconColor} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
});

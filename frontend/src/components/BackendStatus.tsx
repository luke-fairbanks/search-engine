import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardBody, Spinner } from '@nextui-org/react';
import { searchApi } from '../services/api';

interface BackendStatusProps {
  onStatusChange?: (isOnline: boolean) => void;
}

const BackendStatus: React.FC<BackendStatusProps> = ({ onStatusChange }) => {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  const checkHealth = async () => {
    try {
      const healthy = await searchApi.health();
      setIsOnline(healthy);
      onStatusChange?.(healthy);
      
      if (healthy) {
        setRetryCount(0);
        setIsChecking(false);
      } else {
        setRetryCount(prev => prev + 1);
      }
    } catch (error) {
      setIsOnline(false);
      onStatusChange?.(false);
      setRetryCount(prev => prev + 1);
    }
  };

  useEffect(() => {
    // Initial check
    checkHealth();

    // Poll more frequently when offline
    const interval = setInterval(() => {
      if (!isOnline) {
        checkHealth();
      } else {
        // Periodic health check when online
        checkHealth();
      }
    }, isOnline ? 30000 : 3000); // 30s when online, 3s when offline

    return () => clearInterval(interval);
  }, [isOnline]);

  // Don't show anything if backend is online
  if (isOnline === true) {
    return null;
  }

  // Show loading state when initially checking or backend is waking up
  if (isOnline === false || isOnline === null) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4"
      >
        <Card className="bg-gradient-to-r from-blue-500/90 to-purple-500/90 backdrop-blur-lg border border-white/20">
          <CardBody className="py-4">
            <div className="flex items-center gap-4">
              <Spinner size="sm" color="white" />
              <div className="flex-1">
                <div className="text-white font-semibold text-sm">
                  {retryCount === 0 ? 'Connecting to backend...' : 'Backend is waking up...'}
                </div>
                <div className="text-white/80 text-xs mt-1">
                  {retryCount === 0 
                    ? 'Checking server status'
                    : `This may take 30-60 seconds (attempt ${retryCount})`
                  }
                </div>
              </div>
            </div>
          </CardBody>
        </Card>
      </motion.div>
    );
  }

  return null;
};

export default BackendStatus;

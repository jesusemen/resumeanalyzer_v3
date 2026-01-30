import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { LogOut, User, FileText, TrendingUp, Settings, CreditCard, Crown } from 'lucide-react';
import ResumeAnalyzer from './ResumeAnalyzer';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
  };

  const handleUpgrade = () => {
    navigate('/payment');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Resume Analyzer
                </h1>
                <p className="text-sm text-gray-600">AI-Powered Resume Analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                onClick={handleUpgrade}
                variant="outline"
                size="sm"
                className="border-orange-300 hover:bg-orange-50 text-orange-600 hover:text-orange-700"
              >
                <Crown className="w-4 h-4 mr-2" />
                Upgrade to Premium
              </Button>
              
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">
                  {user?.full_name || user?.email}
                </span>
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Free
                </Badge>
              </div>
              
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="border-gray-300 hover:bg-gray-50"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="grid md:grid-cols-4 gap-6">
            <Card className="bg-white/60 backdrop-blur-sm border-blue-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Analysis Ready
                </CardTitle>
                <CardDescription>
                  Upload documents to start analyzing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">Ready</div>
                <p className="text-sm text-gray-600 mt-1">
                  AI-powered analysis available
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/60 backdrop-blur-sm border-purple-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <FileText className="w-5 h-5 text-purple-600" />
                  Document Support
                </CardTitle>
                <CardDescription>
                  Supported file formats
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">PDF, DOC</div>
                <p className="text-sm text-gray-600 mt-1">
                  Multiple formats supported
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/60 backdrop-blur-sm border-green-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Settings className="w-5 h-5 text-green-600" />
                  Account Status
                </CardTitle>
                <CardDescription>
                  Your account information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">Active</div>
                <p className="text-sm text-gray-600 mt-1">
                  Free tier enabled
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-orange-100 to-yellow-100 border-orange-200 cursor-pointer hover:shadow-lg transition-shadow" onClick={handleUpgrade}>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <CreditCard className="w-5 h-5 text-orange-600" />
                  Upgrade Plan
                </CardTitle>
                <CardDescription>
                  Unlock premium features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">$2</div>
                <p className="text-sm text-orange-700 mt-1">
                  One-time payment
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Resume Analyzer Component */}
        <ResumeAnalyzer />
      </div>
    </div>
  );
};

export default Dashboard;
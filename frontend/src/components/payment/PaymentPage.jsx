import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { 
  CreditCard, 
  Lock, 
  Shield, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Zap,
  Globe,
  DollarSign
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PaymentPage = () => {
  const [selectedProvider, setSelectedProvider] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const paymentProviders = [
    {
      id: 'stripe',
      name: 'Stripe',
      description: 'International payment processing',
      icon: <Globe className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-blue-500 to-purple-600',
      supported: ['Credit Cards', 'Debit Cards', 'Digital Wallets'],
      disabled: true
    },
    {
      id: 'paystack',
      name: 'Paystack',
      description: 'African payment gateway',
      icon: <Zap className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-green-500 to-teal-600',
      supported: ['Bank Transfer', 'Card Payments', 'Mobile Money'],
      disabled: true
    },
    {
      id: 'interswitch',
      name: 'Interswitch',
      description: 'Nigerian payment solutions',
      icon: <DollarSign className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-orange-500 to-red-600',
      supported: ['Verve Cards', 'Bank Transfer', 'USSD'],
      disabled: true
    }
  ];

  const handlePaymentSelect = (providerId) => {
    setSelectedProvider(providerId);
  };

  const handlePayment = async () => {
    if (!selectedProvider) {
      toast({
        title: "No Payment Method Selected",
        description: "Please select a payment provider to continue.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);

    // Simulate payment processing
    setTimeout(() => {
      setIsProcessing(false);
      toast({
        title: "Payment System Disabled",
        description: "Payment functionality is currently disabled. This is a demo version.",
        variant: "destructive",
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="mb-4 hover:bg-white/50"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          
          <div className="text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
              Upgrade Your Plan
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Choose your payment method to unlock premium features and unlimited resume analysis.
            </p>
          </div>
        </div>

        {/* Pricing Card */}
        <Card className="mb-8 bg-white/80 backdrop-blur-sm border-2 border-blue-200">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-blue-600">Premium Plan</CardTitle>
            <CardDescription>
              <div className="text-4xl font-bold text-gray-800 mb-2">$2</div>
              <div className="text-gray-600">One-time payment • Unlimited access</div>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">What's Included:</h3>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Unlimited resume analysis</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>AI-powered candidate ranking</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Detailed analysis reports</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Export results to PDF/CSV</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Priority customer support</span>
                  </li>
                </ul>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Shield className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-blue-600">Secure & Trusted</h3>
                </div>
                <p className="text-sm text-blue-700">
                  Your payment information is encrypted and secure. We support multiple 
                  payment methods for your convenience.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Payment Methods */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Choose Payment Method</h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {paymentProviders.map((provider) => (
              <Card 
                key={provider.id}
                className={`cursor-pointer transition-all duration-300 ${
                  selectedProvider === provider.id 
                    ? 'ring-2 ring-blue-500 bg-blue-50' 
                    : 'hover:shadow-lg bg-white/60 backdrop-blur-sm'
                } ${provider.disabled ? 'opacity-60' : ''}`}
                onClick={() => !provider.disabled && handlePaymentSelect(provider.id)}
              >
                <CardHeader className="text-center">
                  <div className={`mx-auto w-16 h-16 ${provider.color} rounded-xl flex items-center justify-center mb-4`}>
                    {provider.icon}
                  </div>
                  <CardTitle className="text-lg flex items-center justify-center gap-2">
                    {provider.name}
                    {provider.disabled && (
                      <Badge variant="secondary" className="bg-red-100 text-red-800">
                        Disabled
                      </Badge>
                    )}
                  </CardTitle>
                  <CardDescription>{provider.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {provider.supported.map((method, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        {method}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Payment Button */}
        <Card className="bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Lock className="w-5 h-5 text-gray-500" />
                <span className="text-sm text-gray-600">
                  SSL encrypted • Secure payment processing
                </span>
              </div>
              
              <Button
                onClick={handlePayment}
                disabled={!selectedProvider || isProcessing}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-semibold rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <CreditCard className="w-5 h-5 mr-2" />
                    Pay $2 Now
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Disabled Notice */}
        <div className="mt-8 p-4 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-orange-600" />
            <h3 className="font-semibold text-orange-800">Demo Mode</h3>
          </div>
          <p className="text-sm text-orange-700">
            Payment functionality is currently disabled. This is a demonstration version 
            of the payment integration system. In production, this would connect to real 
            payment providers (Stripe, Paystack, and Interswitch).
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;
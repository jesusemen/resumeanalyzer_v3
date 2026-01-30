import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Progress } from './ui/progress';
import { FileText, Upload, Users, Award, Phone, Mail, User } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const ResumeAnalyzer = () => {
  const [jobDescription, setJobDescription] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [results, setResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const { toast } = useToast();

  const handleJobDescriptionUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type === 'application/pdf' || file.type === 'application/msword' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setJobDescription(file);
        toast({
          title: "Job Description Uploaded",
          description: `${file.name} has been uploaded successfully.`,
        });
      } else {
        toast({
          title: "Invalid File Type",
          description: "Please upload a PDF or Word document.",
          variant: "destructive",
        });
      }
    }
  };

  const handleResumeUpload = (event) => {
    const files = Array.from(event.target.files);
    if (files.length >= 5 && files.length <= 30) {
      setResumes(files);
      toast({
        title: "Resumes Uploaded",
        description: `${files.length} resumes have been uploaded successfully.`,
      });
    } else if (files.length < 5) {
      toast({
        title: "Insufficient Resumes",
        description: "Please upload at least 5 resumes for analysis.",
        variant: "destructive",
      });
    } else if (files.length > 30) {
      toast({
        title: "Too Many Resumes",
        description: "Please upload maximum 30 resumes at once.",
        variant: "destructive",
      });
    }
  };

  const handleAnalyze = async () => {
    if (!jobDescription || resumes.length < 5 || resumes.length > 30) {
      toast({
        title: "Missing or Invalid Files",
        description: "Please upload a job description and 5-30 resumes.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('job_description', jobDescription);
      
      resumes.forEach((resume) => {
        formData.append('resumes', resume);
      });

      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await axios.post(`${BACKEND_URL}/api/analyze-resumes`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResults(response.data.data);
        toast({
          title: "Analysis Complete",
          description: "Resume analysis completed successfully!",
        });
      } else {
        throw new Error(response.data.message || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis Failed",
        description: error.response?.data?.detail || "An error occurred during analysis.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getRankBadgeColor = (rank) => {
    if (rank <= 3) return 'bg-gradient-to-r from-yellow-400 to-orange-500';
    if (rank <= 5) return 'bg-gradient-to-r from-blue-400 to-blue-600';
    return 'bg-gradient-to-r from-gray-400 to-gray-600';
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            AI Resume Analyzer
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload a job description and candidate resumes to get intelligent matching analysis with detailed rankings and insights.
          </p>
        </div>

        {/* Upload Section */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="border-2 border-dashed border-blue-200 hover:border-blue-400 transition-colors">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                Job Description
              </CardTitle>
              <CardDescription>
                Upload the job description (PDF or Word document)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Label htmlFor="job-description" className="text-sm font-medium">
                  Select Job Description File
                </Label>
                <Input
                  id="job-description"
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleJobDescriptionUpload}
                  className="cursor-pointer"
                />
                {jobDescription && (
                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <FileText className="w-4 h-4" />
                    {jobDescription.name}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-dashed border-purple-200 hover:border-purple-400 transition-colors">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-purple-600" />
                Candidate Resumes
              </CardTitle>
              <CardDescription>
                Upload candidate resumes (5-30 files required)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Label htmlFor="resumes" className="text-sm font-medium">
                  Select Resume Files (5-30 files required)
                </Label>
                <Input
                  id="resumes"
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx"
                  onChange={handleResumeUpload}
                  className="cursor-pointer"
                />
                {resumes.length > 0 && (
                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <Upload className="w-4 h-4" />
                    {resumes.length} resumes uploaded
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Analyze Button */}
        <div className="text-center mb-8">
          <Button
            onClick={handleAnalyze}
            disabled={!jobDescription || resumes.length < 5 || resumes.length > 30 || isAnalyzing}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-semibold rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Analyzing Resumes...
              </>
            ) : (
              <>
                <Award className="w-5 h-5 mr-2" />
                Analyze & Rank Candidates
              </>
            )}
          </Button>
        </div>

        {/* Results Section */}
        {results && (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Analysis Results</h2>
              <p className="text-gray-600">Top 7 candidates ranked by job fit</p>
            </div>

            <div className="grid gap-4">
              {results.candidates.map((candidate, index) => (
                <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <Badge className={`${getRankBadgeColor(candidate.rank)} text-white px-3 py-1 text-lg font-bold`}>
                          #{candidate.rank}
                        </Badge>
                        <div>
                          <h3 className="text-xl font-semibold text-gray-800">{candidate.name}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                            <div className="flex items-center gap-1">
                              <Mail className="w-4 h-4" />
                              {candidate.email}
                            </div>
                            <div className="flex items-center gap-1">
                              <Phone className="w-4 h-4" />
                              {candidate.phone}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-3xl font-bold ${getScoreColor(candidate.score)}`}>
                          {candidate.score}%
                        </div>
                        <p className="text-sm text-gray-500">Match Score</p>
                      </div>
                    </div>

                    <div className="mb-4">
                      <Progress value={candidate.score} className="h-2" />
                    </div>

                    <Separator className="my-4" />

                    <div>
                      <h4 className="font-semibold text-gray-700 mb-2">Ranking Reasons:</h4>
                      <ul className="space-y-1 text-sm text-gray-600">
                        {candidate.reasons.map((reason, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-blue-500 mt-1">•</span>
                            {reason}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {results.noMatch && (
              <Card className="border-2 border-red-200 bg-red-50">
                <CardContent className="p-6 text-center">
                  <div className="text-red-600 text-lg font-semibold mb-2">
                    No Match Found
                  </div>
                  <p className="text-red-700">
                    No candidates met the minimum requirements for this position.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeAnalyzer;
import React, { useState } from 'react';
import { Upload, FileText, Download, Loader2, Heart, Apple, Activity, AlertCircle } from 'lucide-react';

const DietPlanGenerator = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [dietPlan, setDietPlan] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    if (uploadedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    setFile(uploadedFile);
    setError(null);
    setDietPlan(null);
  };

  const analyzeMedicalReport = async () => {
    if (!file) return;

    setLoading(true);
    setAnalyzing(true);
    setError(null);

    try {
      // Read the PDF file
      const base64Data = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsDataURL(file);
      });

      // Call Claude API to analyze the medical report
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 4000,
          messages: [
            {
              role: 'user',
              content: [
                {
                  type: 'document',
                  source: {
                    type: 'base64',
                    media_type: 'application/pdf',
                    data: base64Data
                  }
                },
                {
                  type: 'text',
                  text: `Analyze this medical report and create a comprehensive personalized diet plan. 

Please extract and analyze:
1. Key health metrics (blood sugar, cholesterol, vitamins, minerals, etc.)
2. Medical conditions or concerns identified
3. Any deficiencies or abnormal values

Then provide a detailed response in JSON format with this structure:
{
  "patientInfo": {
    "conditions": ["list of identified conditions"],
    "deficiencies": ["list of deficiencies"],
    "keyMetrics": {"metric": "value and status"}
  },
  "dietaryRecommendations": {
    "foodsToInclude": ["detailed list with reasons"],
    "foodsToAvoid": ["detailed list with reasons"],
    "supplementsSuggested": ["list if needed"]
  },
  "mealPlan": {
    "breakfast": ["option 1", "option 2", "option 3"],
    "lunch": ["option 1", "option 2", "option 3"],
    "dinner": ["option 1", "option 2", "option 3"],
    "snacks": ["option 1", "option 2", "option 3"]
  },
  "nutritionGuidelines": {
    "dailyCalories": "recommended range",
    "macroDistribution": {"protein": "x%", "carbs": "y%", "fats": "z%"},
    "hydration": "water intake recommendation"
  },
  "lifestyle": {
    "exerciseRecommendations": "exercise suggestions",
    "sleepGuidelines": "sleep recommendations",
    "stressManagement": "stress tips"
  },
  "warnings": ["important precautions or warnings"],
  "generalAdvice": "overall health advice"
}

Ensure all recommendations are evidence-based and appropriate for the conditions identified.`
                }
              ]
            }
          ]
        })
      });

      const data = await response.json();
      
      if (!data.content || data.content.length === 0) {
        throw new Error('No response from AI');
      }

      // Extract text from response
      const textContent = data.content
        .filter(item => item.type === 'text')
        .map(item => item.text)
        .join('\n');

      // Parse JSON from the response
      const jsonMatch = textContent.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('Could not parse diet plan from response');
      }

      const parsedPlan = JSON.parse(jsonMatch[0]);
      setDietPlan(parsedPlan);
      setAnalyzing(false);
      
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to analyze the report. Please try again or ensure the PDF contains medical data.');
      setAnalyzing(false);
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    if (!dietPlan) return;

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Personalized Diet Plan</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }
            h1 { color: #10b981; border-bottom: 3px solid #10b981; padding-bottom: 10px; }
            h2 { color: #059669; margin-top: 30px; }
            h3 { color: #047857; margin-top: 20px; }
            .section { margin-bottom: 30px; }
            .warning { background: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; margin: 20px 0; }
            ul { list-style-type: disc; margin-left: 20px; }
            .metric { background: #f0fdf4; padding: 10px; margin: 5px 0; border-radius: 5px; }
            .meal-option { background: #f9fafb; padding: 8px; margin: 5px 0; border-left: 3px solid #10b981; }
          </style>
        </head>
        <body>
          <h1>🍏 Personalized Diet Plan</h1>
          <p><em>Generated on ${new Date().toLocaleDateString()}</em></p>
          
          ${dietPlan.warnings && dietPlan.warnings.length > 0 ? `
            <div class="warning">
              <h3>⚠️ Important Warnings</h3>
              <ul>${dietPlan.warnings.map(w => `<li>${w}</li>`).join('')}</ul>
            </div>
          ` : ''}
          
          <div class="section">
            <h2>📊 Health Analysis</h2>
            <h3>Identified Conditions</h3>
            <ul>${dietPlan.patientInfo.conditions.map(c => `<li>${c}</li>`).join('')}</ul>
            
            ${dietPlan.patientInfo.deficiencies.length > 0 ? `
              <h3>Deficiencies</h3>
              <ul>${dietPlan.patientInfo.deficiencies.map(d => `<li>${d}</li>`).join('')}</ul>
            ` : ''}
            
            <h3>Key Metrics</h3>
            ${Object.entries(dietPlan.patientInfo.keyMetrics).map(([k, v]) => 
              `<div class="metric"><strong>${k}:</strong> ${v}</div>`
            ).join('')}
          </div>
          
          <div class="section">
            <h2>🥗 Dietary Recommendations</h2>
            <h3>Foods to Include</h3>
            <ul>${dietPlan.dietaryRecommendations.foodsToInclude.map(f => `<li>${f}</li>`).join('')}</ul>
            
            <h3>Foods to Avoid</h3>
            <ul>${dietPlan.dietaryRecommendations.foodsToAvoid.map(f => `<li>${f}</li>`).join('')}</ul>
            
            ${dietPlan.dietaryRecommendations.supplementsSuggested.length > 0 ? `
              <h3>Suggested Supplements</h3>
              <ul>${dietPlan.dietaryRecommendations.supplementsSuggested.map(s => `<li>${s}</li>`).join('')}</ul>
            ` : ''}
          </div>
          
          <div class="section">
            <h2>🍽️ Sample Meal Plan</h2>
            <h3>Breakfast Options</h3>
            ${dietPlan.mealPlan.breakfast.map((m, i) => `<div class="meal-option">${i + 1}. ${m}</div>`).join('')}
            
            <h3>Lunch Options</h3>
            ${dietPlan.mealPlan.lunch.map((m, i) => `<div class="meal-option">${i + 1}. ${m}</div>`).join('')}
            
            <h3>Dinner Options</h3>
            ${dietPlan.mealPlan.dinner.map((m, i) => `<div class="meal-option">${i + 1}. ${m}</div>`).join('')}
            
            <h3>Snack Options</h3>
            ${dietPlan.mealPlan.snacks.map((m, i) => `<div class="meal-option">${i + 1}. ${m}</div>`).join('')}
          </div>
          
          <div class="section">
            <h2>📈 Nutrition Guidelines</h2>
            <p><strong>Daily Calories:</strong> ${dietPlan.nutritionGuidelines.dailyCalories}</p>
            <p><strong>Macro Distribution:</strong></p>
            <ul>
              ${Object.entries(dietPlan.nutritionGuidelines.macroDistribution).map(([k, v]) => 
                `<li>${k.charAt(0).toUpperCase() + k.slice(1)}: ${v}</li>`
              ).join('')}
            </ul>
            <p><strong>Hydration:</strong> ${dietPlan.nutritionGuidelines.hydration}</p>
          </div>
          
          <div class="section">
            <h2>💪 Lifestyle Recommendations</h2>
            <p><strong>Exercise:</strong> ${dietPlan.lifestyle.exerciseRecommendations}</p>
            <p><strong>Sleep:</strong> ${dietPlan.lifestyle.sleepGuidelines}</p>
            <p><strong>Stress Management:</strong> ${dietPlan.lifestyle.stressManagement}</p>
          </div>
          
          <div class="section">
            <h2>💡 General Advice</h2>
            <p>${dietPlan.generalAdvice}</p>
          </div>
          
          <hr style="margin-top: 40px; border: none; border-top: 2px solid #e5e7eb;">
          <p style="text-align: center; color: #6b7280; font-size: 0.9em; margin-top: 20px;">
            <strong>Disclaimer:</strong> This diet plan is AI-generated based on medical report analysis. 
            Please consult with healthcare professionals before making significant dietary changes.
          </p>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const exportToJSON = () => {
    if (!dietPlan) return;

    const dataStr = JSON.stringify(dietPlan, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `diet-plan-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Heart className="w-12 h-12 text-green-600" />
            <h1 className="text-4xl font-bold text-gray-800">AI Diet Plan Generator</h1>
          </div>
          <p className="text-lg text-gray-600">Upload your medical report for personalized nutrition recommendations</p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex flex-col items-center">
            <label className="w-full cursor-pointer">
              <div className="border-3 border-dashed border-green-300 rounded-xl p-12 text-center hover:border-green-500 hover:bg-green-50 transition-all">
                <Upload className="w-16 h-16 text-green-600 mx-auto mb-4" />
                <p className="text-xl font-semibold text-gray-700 mb-2">
                  {file ? file.name : 'Click to upload medical report (PDF)'}
                </p>
                <p className="text-sm text-gray-500">Blood tests, health checkups, or medical reports</p>
              </div>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {file && !dietPlan && (
              <button
                onClick={analyzeMedicalReport}
                disabled={loading}
                className="mt-6 bg-green-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-3 transition-all shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    Analyzing Report...
                  </>
                ) : (
                  <>
                    <Activity className="w-6 h-6" />
                    Generate Diet Plan
                  </>
                )}
              </button>
            )}
          </div>

          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Analysis Progress */}
        {analyzing && !dietPlan && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <div className="text-center">
              <Loader2 className="w-16 h-16 text-green-600 animate-spin mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Analyzing Your Medical Report</h3>
              <p className="text-gray-600">AI is extracting health metrics and creating personalized recommendations...</p>
            </div>
          </div>
        )}

        {/* Diet Plan Results */}
        {dietPlan && (
          <div className="space-y-6">
            {/* Export Buttons */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="flex gap-4 justify-center">
                <button
                  onClick={exportToPDF}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center gap-2 transition-all shadow-md hover:shadow-lg"
                >
                  <FileText className="w-5 h-5" />
                  Export as PDF
                </button>
                <button
                  onClick={exportToJSON}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 flex items-center gap-2 transition-all shadow-md hover:shadow-lg"
                >
                  <Download className="w-5 h-5" />
                  Export as JSON
                </button>
              </div>
            </div>

            {/* Warnings */}
            {dietPlan.warnings && dietPlan.warnings.length > 0 && (
              <div className="bg-amber-50 border-l-4 border-amber-500 rounded-lg p-6 shadow-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-amber-900 mb-2">Important Warnings</h3>
                    <ul className="list-disc list-inside space-y-1 text-amber-800">
                      {dietPlan.warnings.map((warning, idx) => (
                        <li key={idx}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Health Analysis */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <Activity className="w-7 h-7 text-green-600" />
                Health Analysis
              </h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">Identified Conditions</h3>
                  <div className="flex flex-wrap gap-2">
                    {dietPlan.patientInfo.conditions.map((condition, idx) => (
                      <span key={idx} className="bg-red-100 text-red-800 px-4 py-2 rounded-full text-sm font-medium">
                        {condition}
                      </span>
                    ))}
                  </div>
                </div>

                {dietPlan.patientInfo.deficiencies.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">Deficiencies</h3>
                    <div className="flex flex-wrap gap-2">
                      {dietPlan.patientInfo.deficiencies.map((def, idx) => (
                        <span key={idx} className="bg-orange-100 text-orange-800 px-4 py-2 rounded-full text-sm font-medium">
                          {def}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">Key Metrics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(dietPlan.patientInfo.keyMetrics).map(([metric, value]) => (
                      <div key={metric} className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <span className="font-semibold text-gray-700">{metric}:</span>
                        <span className="text-gray-600 ml-2">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Dietary Recommendations */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <Apple className="w-7 h-7 text-green-600" />
                Dietary Recommendations
              </h2>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-green-700 mb-3">✅ Foods to Include</h3>
                  <ul className="space-y-2">
                    {dietPlan.dietaryRecommendations.foodsToInclude.map((food, idx) => (
                      <li key={idx} className="bg-green-50 p-3 rounded-lg border-l-4 border-green-500 text-gray-700">
                        {food}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-red-700 mb-3">❌ Foods to Avoid</h3>
                  <ul className="space-y-2">
                    {dietPlan.dietaryRecommendations.foodsToAvoid.map((food, idx) => (
                      <li key={idx} className="bg-red-50 p-3 rounded-lg border-l-4 border-red-500 text-gray-700">
                        {food}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {dietPlan.dietaryRecommendations.supplementsSuggested.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-blue-700 mb-3">💊 Suggested Supplements</h3>
                  <div className="flex flex-wrap gap-2">
                    {dietPlan.dietaryRecommendations.supplementsSuggested.map((supp, idx) => (
                      <span key={idx} className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium">
                        {supp}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Meal Plan */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">🍽️ Sample Meal Plan</h2>
              
              <div className="grid md:grid-cols-2 gap-6">
                {Object.entries(dietPlan.mealPlan).map(([mealType, options]) => (
                  <div key={mealType}>
                    <h3 className="text-lg font-semibold text-gray-700 mb-3 capitalize">
                      {mealType}
                    </h3>
                    <div className="space-y-2">
                      {options.map((option, idx) => (
                        <div key={idx} className="bg-gray-50 p-3 rounded-lg border-l-4 border-green-400">
                          <span className="font-medium text-green-700">Option {idx + 1}:</span>
                          <span className="text-gray-700 ml-2">{option}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Nutrition Guidelines */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">📈 Nutrition Guidelines</h2>
              
              <div className="space-y-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <span className="font-semibold text-gray-700">Daily Calories:</span>
                  <span className="text-gray-600 ml-2">{dietPlan.nutritionGuidelines.dailyCalories}</span>
                </div>

                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="font-semibold text-gray-700 mb-2">Macro Distribution:</p>
                  <div className="grid grid-cols-3 gap-3">
                    {Object.entries(dietPlan.nutritionGuidelines.macroDistribution).map(([macro, percentage]) => (
                      <div key={macro} className="text-center">
                        <div className="bg-white p-3 rounded-lg shadow-sm">
                          <p className="text-sm text-gray-600 capitalize">{macro}</p>
                          <p className="text-xl font-bold text-purple-700">{percentage}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-cyan-50 p-4 rounded-lg">
                  <span className="font-semibold text-gray-700">Hydration:</span>
                  <span className="text-gray-600 ml-2">{dietPlan.nutritionGuidelines.hydration}</span>
                </div>
              </div>
            </div>

            {/* Lifestyle Recommendations */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">💪 Lifestyle Recommendations</h2>
              
              <div className="space-y-4">
                <div className="bg-orange-50 p-4 rounded-lg">
                  <p className="font-semibold text-gray-700 mb-2">🏃 Exercise:</p>
                  <p className="text-gray-600">{dietPlan.lifestyle.exerciseRecommendations}</p>
                </div>

                <div className="bg-indigo-50 p-4 rounded-lg">
                  <p className="font-semibold text-gray-700 mb-2">😴 Sleep:</p>
                  <p className="text-gray-600">{dietPlan.lifestyle.sleepGuidelines}</p>
                </div>

                <div className="bg-pink-50 p-4 rounded-lg">
                  <p className="font-semibold text-gray-700 mb-2">🧘 Stress Management:</p>
                  <p className="text-gray-600">{dietPlan.lifestyle.stressManagement}</p>
                </div>
              </div>
            </div>

            {/* General Advice */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl shadow-xl p-8 border-2 border-green-200">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">💡 General Advice</h2>
              <p className="text-gray-700 leading-relaxed">{dietPlan.generalAdvice}</p>
            </div>

            {/* Disclaimer */}
            <div className="bg-gray-100 rounded-lg p-6 text-center">
              <p className="text-sm text-gray-600">
                <strong>Disclaimer:</strong> This diet plan is AI-generated based on medical report analysis. 
                Please consult with healthcare professionals before making significant dietary changes.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DietPlanGenerator;

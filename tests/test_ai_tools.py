"""
Test suite for AI integration and tools
Testing the revolutionary N1O1ai assistant capabilities
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from routes.ai_tools import ai_tools_bp, claude_completion, validate_request

class TestAITools:
    """Test AI tools and Claude integration"""
    
    def test_validate_request(self):
        """Test request validation logic"""
        # Valid request
        valid, msg = validate_request({"field1": "value1", "field2": "value2"}, ["field1", "field2"])
        assert valid is True
        assert msg == ""
        
        # Missing fields
        valid, msg = validate_request({"field1": "value1"}, ["field1", "field2"])
        assert valid is False
        assert "field2" in msg
        
        # Empty request
        valid, msg = validate_request(None, ["field1"])
        assert valid is False
        assert "No data provided" in msg
    
    @patch('routes.ai_tools.client.messages.create')
    def test_claude_completion_success(self, mock_create):
        """Test successful Claude API call"""
        # Mock response
        mock_message = Mock()
        mock_message.content = [Mock(text="Test response from Claude")]
        mock_create.return_value = mock_message
        
        response = claude_completion("Test prompt")
        
        assert response == "Test response from Claude"
        mock_create.assert_called_once()
        
    @patch('routes.ai_tools.client.messages.create')
    def test_claude_completion_retry_on_rate_limit(self, mock_create):
        """Test retry logic on rate limit errors"""
        from anthropic import RateLimitError
        
        # First call raises RateLimitError, second succeeds
        mock_message = Mock()
        mock_message.content = [Mock(text="Success after retry")]
        mock_create.side_effect = [
            RateLimitError("Rate limit exceeded", response=Mock(), body={}),
            mock_message
        ]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            response = claude_completion("Test prompt")
        
        assert response == "Success after retry"
        assert mock_create.call_count == 2
    
    def test_pre_screening_endpoint_structure(self):
        """Test pre-screening endpoint request/response structure"""
        with ai_tools_bp.app.test_client() as client:
            # Test data
            test_data = {
                "patient_data": {
                    "age": 45,
                    "medical_history": "No significant history",
                    "current_medications": ["aspirin"],
                    "vital_signs": {"bp": "120/80", "hr": 72},
                    "lab_results": {"hemoglobin": 14.5, "creatinine": 1.0}
                },
                "trial_criteria": {
                    "inclusion": ["Age 18-65", "Healthy volunteer"],
                    "exclusion": ["Pregnancy", "Severe hypertension"]
                }
            }
            
            # Mock Claude response
            with patch('routes.ai_tools.claude_completion') as mock_claude:
                mock_claude.return_value = json.dumps({
                    "eligibility_status": "eligible",
                    "criteria_met": ["Age 18-65", "Healthy volunteer"],
                    "criteria_not_met": [],
                    "additional_info_needed": ["NO2 baseline levels"],
                    "recommendations": ["Proceed with baseline testing"]
                })
                
                response = client.post('/api/ai-tools/pre-screening',
                                     json=test_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert 'result' in data
                assert data['result']['eligibility_status'] == 'eligible'
    
    def test_generate_note_endpoint(self):
        """Test clinical note generation endpoint"""
        with ai_tools_bp.app.test_client() as client:
            test_data = {
                "patient_info": {
                    "name": "John Doe",
                    "age": 35,
                    "gender": "Male"
                },
                "visit_data": {
                    "visit_type": "Initial Assessment",
                    "date": "2025-01-14",
                    "chief_complaint": "Clinical trial enrollment",
                    "vitals": {"bp": "118/76", "hr": 68, "temp": 98.6},
                    "observations": ["Alert and oriented", "No acute distress"]
                },
                "note_type": "progress"
            }
            
            with patch('routes.ai_tools.claude_completion') as mock_claude:
                mock_claude.return_value = "SOAP Note generated successfully..."
                
                response = client.post('/api/ai-tools/generate-note',
                                     json=test_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert 'note' in data
    
    def test_patient_sentiment_analysis(self):
        """Test patient sentiment analysis endpoint"""
        with ai_tools_bp.app.test_client() as client:
            test_data = {
                "patient_id": "P001",
                "feedback_text": "The treatment has been very effective. I feel much better and have more energy throughout the day.",
                "feedback_source": "survey",
                "feedback_date": "2025-01-14"
            }
            
            with patch('routes.ai_tools.claude_completion') as mock_claude:
                mock_claude.return_value = json.dumps({
                    "sentiment": "positive",
                    "sentiment_score": 0.85,
                    "key_themes": ["treatment effectiveness", "improved energy"],
                    "concerns": [],
                    "positive_points": ["effective treatment", "increased energy"],
                    "suggestions": []
                })
                
                response = client.post('/api/ai-tools/patient-sentiment',
                                     json=test_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert data['analysis']['sentiment'] == 'positive'
                assert data['analysis']['sentiment_score'] > 0
    
    def test_dynamic_consent_generation(self):
        """Test dynamic consent form generation"""
        with ai_tools_bp.app.test_client() as client:
            test_data = {
                "patient_demographics": {
                    "age": 25,
                    "education_level": "college",
                    "language_preference": "English",
                    "medical_literacy": "medium"
                },
                "trial_info": {
                    "trial_name": "N1O1 Phase II Trial",
                    "treatment_description": "Nitric oxide supplementation study",
                    "risks": ["Mild headache", "Temporary hypotension"],
                    "benefits": ["Improved blood flow", "Potential cardiovascular benefits"],
                    "duration": "12 weeks",
                    "procedures": ["Weekly blood draws", "Daily supplement intake"]
                },
                "format_type": "simplified"
            }
            
            with patch('routes.ai_tools.claude_completion') as mock_claude:
                mock_claude.return_value = "Simplified consent form content..."
                
                response = client.post('/api/ai-tools/dynamic-consent',
                                     json=test_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert 'consent_form' in data
    
    def test_research_insight_generator(self):
        """Test research insight generation with visualization"""
        with ai_tools_bp.app.test_client() as client:
            test_data = {
                "research_data": {
                    "trial_results": {
                        "n_participants": 50,
                        "mean_no2_increase": 3.2,
                        "response_rate": 0.78
                    },
                    "simulation_data": [
                        {"time": 0, "value": 0.2},
                        {"time": 30, "value": 3.8},
                        {"time": 60, "value": 2.5},
                        {"time": 90, "value": 1.5}
                    ],
                    "related_research": ["Smith et al. 2024 - NO pathways"],
                    "observed_effects": ["Vasodilation", "Improved endothelial function"]
                },
                "focus_areas": ["mechanism of action", "clinical applications"],
                "insight_type": "comprehensive"
            }
            
            with patch('routes.ai_tools.claude_completion') as mock_claude:
                mock_claude.return_value = "Comprehensive analysis of nitric oxide research..."
                
                response = client.post('/api/ai-tools/research-insight',
                                     json=test_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert 'insights' in data
                # Visualization should be generated for simulation data
                assert 'visualization' in data
    
    def test_ai_report_writer(self):
        """Test AI report generation for different audiences"""
        with ai_tools_bp.app.test_client() as client:
            test_data = {
                "trial_data": {
                    "trial_name": "N1O1 Phase II",
                    "trial_phase": "Phase II",
                    "participants": 100,
                    "treatment_groups": ["Placebo", "30mg N1O1", "60mg N1O1"],
                    "outcome_measures": ["Plasma NO2 levels", "Blood pressure", "Endothelial function"],
                    "results_summary": {
                        "primary_endpoint_met": True,
                        "mean_no2_increase": "3.5 µM",
                        "bp_reduction": "8/5 mmHg",
                        "adverse_events": "Mild, self-limiting"
                    }
                },
                "report_type": "abstract",
                "audience": "researchers"
            }
            
            with patch('routes.ai_tools.claude_completion') as mock_claude:
                mock_claude.return_value = "Abstract: Background: Nitric oxide..."
                
                response = client.post('/api/ai-tools/ai-report-writer',
                                     json=test_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert 'report' in data
    
    def test_error_handling_invalid_request(self):
        """Test error handling for invalid requests"""
        with ai_tools_bp.app.test_client() as client:
            # Missing required fields
            response = client.post('/api/ai-tools/pre-screening',
                                 json={"incomplete": "data"},
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'message' in data
    
    def test_visualization_error_handling(self):
        """Test graceful handling of visualization errors"""
        with ai_tools_bp.app.test_client() as client:
            test_data = {
                "research_data": {
                    "simulation_data": "invalid_data_format",  # This should cause viz error
                    "observed_effects": ["Test effect"]
                },
                "insight_type": "comprehensive"
            }
            
            with patch('routes.ai_tools.claude_completion') as mock_claude:
                mock_claude.return_value = "Analysis without visualization..."
                
                response = client.post('/api/ai-tools/research-insight',
                                     json=test_data,
                                     content_type='application/json')
                
                # Should still succeed but without visualization
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert 'visualization' not in data  # No viz on error

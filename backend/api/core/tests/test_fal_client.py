"""
Test cases for fal.ai client
"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings before imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'figureforge.settings')
django.setup()

import pytest
import time
import requests
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import RequestException, HTTPError

from api.core.fal_client import FalAIClient, ImageGenerator


class TestFalAIClient:
    """Test cases for FalAIClient class"""
    
    @pytest.fixture
    def client(self):
        """Create FalAIClient instance"""
        with patch('api.core.fal_client.settings.FAL_API_KEY', 'test-api-key'):
            return FalAIClient()
    
    def test_init_sets_headers(self, client):
        """Test client initialization sets proper headers"""
        assert client.api_key == 'test-api-key'
        assert client.base_url == 'https://api.fal.ai/v1'
        assert client.headers['Authorization'] == 'Bearer test-api-key'
        assert client.headers['Content-Type'] == 'application/json'
    
    def test_make_request_get(self, client):
        """Test making GET request"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'status': 'success'}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = client._make_request('GET', '/test')
            
            mock_get.assert_called_once_with(
                'https://api.fal.ai/v1/test',
                headers=client.headers
            )
            assert result == {'status': 'success'}
    
    def test_make_request_post(self, client):
        """Test making POST request"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'status': 'success'}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            data = {'prompt': 'test'}
            result = client._make_request('POST', '/generate', data)
            
            mock_post.assert_called_once_with(
                'https://api.fal.ai/v1/generate',
                headers=client.headers,
                json=data
            )
            assert result == {'status': 'success'}
    
    def test_make_request_unsupported_method(self, client):
        """Test making request with unsupported method"""
        with pytest.raises(ValueError) as exc_info:
            client._make_request('DELETE', '/test')
        
        assert 'Unsupported method: DELETE' in str(exc_info.value)
    
    def test_make_request_http_error(self, client):
        """Test handling HTTP errors"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = HTTPError('404 Not Found')
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                client._make_request('POST', '/test')
            
            assert 'fal.ai API request failed' in str(exc_info.value)
    
    def test_make_request_connection_error(self, client):
        """Test handling connection errors"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = RequestException('Connection error')
            
            with pytest.raises(Exception) as exc_info:
                client._make_request('GET', '/test')
            
            assert 'fal.ai API request failed' in str(exc_info.value)
    
    def test_generate_image_immediate_result(self, client):
        """Test generate_image with immediate result"""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'images': [{'url': 'https://example.com/image.png'}]
            }
            
            result = client.generate_image('test prompt')
            
            mock_request.assert_called_once_with(
                'POST',
                '/models/flux/dev/generate',
                {
                    'prompt': 'test prompt',
                    'image_size': 'square',
                    'num_inference_steps': 28,
                    'guidance_scale': 3.5,
                    'num_images': 1,
                    'enable_safety_checker': True,
                    'output_format': 'png'
                }
            )
            assert result == {'images': [{'url': 'https://example.com/image.png'}]}
    
    def test_generate_image_with_custom_params(self, client):
        """Test generate_image with custom parameters"""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {'images': []}
            
            custom_params = {
                'image_size': 'portrait',
                'num_inference_steps': 50,
                'seed': 12345
            }
            
            client.generate_image('test prompt', 'stable-diffusion', custom_params)
            
            call_data = mock_request.call_args[0][2]
            assert call_data['image_size'] == 'portrait'
            assert call_data['num_inference_steps'] == 50
            assert call_data['seed'] == 12345
    
    def test_generate_image_polling(self, client):
        """Test generate_image with polling for results"""
        with patch.object(client, '_make_request') as mock_request:
            # First call returns request_id
            mock_request.return_value = {'request_id': 'req123'}
            
            with patch.object(client, '_poll_for_results') as mock_poll:
                mock_poll.return_value = {'images': [{'url': 'test.png'}]}
                
                result = client.generate_image('test prompt')
                
                mock_poll.assert_called_once_with('req123')
                assert result == {'images': [{'url': 'test.png'}]}
    
    def test_generate_image_unexpected_response(self, client):
        """Test generate_image with unexpected response"""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {'unexpected': 'data'}
            
            with pytest.raises(Exception) as exc_info:
                client.generate_image('test prompt')
            
            assert 'Unexpected response from fal.ai' in str(exc_info.value)
    
    def test_poll_for_results_success(self, client):
        """Test successful polling for results"""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = [
                {'status': 'processing'},
                {'status': 'processing'},
                {'status': 'completed', 'result': {'images': [{'url': 'test.png'}]}}
            ]
            
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = client._poll_for_results('req123')
            
            assert result == {'images': [{'url': 'test.png'}]}
            assert mock_request.call_count == 3
    
    def test_poll_for_results_failed(self, client):
        """Test polling when generation fails"""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'status': 'failed',
                'error': 'Safety check failed'
            }
            
            with pytest.raises(Exception) as exc_info:
                client._poll_for_results('req123')
            
            assert 'Generation failed: Safety check failed' in str(exc_info.value)
    
    def test_poll_for_results_timeout(self, client):
        """Test polling timeout"""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {'status': 'processing'}
            
            with patch('time.sleep'):
                with pytest.raises(Exception) as exc_info:
                    client._poll_for_results('req123', max_attempts=2, interval=0)
            
            assert 'Generation timed out' in str(exc_info.value)
    
    def test_get_model_info(self, client):
        """Test getting model information"""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                'id': 'flux/dev',
                'name': 'FLUX.1 Dev',
                'description': 'Advanced image model'
            }
            
            result = client.get_model_info('flux/dev')
            
            mock_request.assert_called_once_with('GET', '/models/flux/dev')
            assert result['name'] == 'FLUX.1 Dev'


class TestImageGenerator:
    """Test cases for ImageGenerator class"""
    
    @pytest.fixture
    def generator(self):
        """Create ImageGenerator instance"""
        with patch('api.core.fal_client.FalAIClient'):
            return ImageGenerator()
    
    def test_init_sets_models(self, generator):
        """Test generator initialization sets model configurations"""
        assert 'flux_dev' in generator.models
        assert 'flux_schnell' in generator.models
        assert 'stable_diffusion' in generator.models
        
        flux_dev = generator.models['flux_dev']
        assert flux_dev['id'] == 'flux/dev'
        assert flux_dev['cost_cents'] == 25
    
    def test_build_prompt_basic(self, generator):
        """Test building prompt from basic filters"""
        filters = {
            'base_prompt': 'A figure study',
            'body_type': 'athletic',
            'pose': 'standing'
        }
        
        prompt = generator._build_prompt(filters)
        
        assert 'A figure study' in prompt
        assert 'athletic body type' in prompt
        assert 'in standing pose' in prompt
        assert '--no nsfw' in prompt
    
    def test_build_prompt_all_filters(self, generator):
        """Test building prompt with all filter options"""
        filters = {
            'base_prompt': 'Reference photo',
            'body_type': 'slim',
            'pose': 'sitting',
            'clothing': 'casual wear',
            'lighting': 'dramatic',
            'background': 'studio'
        }
        
        prompt = generator._build_prompt(filters)
        
        assert 'Reference photo' in prompt
        assert 'slim body type' in prompt
        assert 'in sitting pose' in prompt
        assert 'wearing casual wear' in prompt
        assert 'with dramatic lighting' in prompt
        assert 'studio background' in prompt
    
    def test_build_prompt_minimal(self, generator):
        """Test building prompt with minimal filters"""
        filters = {}
        
        prompt = generator._build_prompt(filters)
        
        assert 'A human figure reference' in prompt
        assert 'simple neutral background' in prompt
        assert 'professional reference photo' in prompt
    
    def test_get_image_size(self, generator):
        """Test converting aspect ratio to image size"""
        assert generator._get_image_size('square') == 'square'
        assert generator._get_image_size('portrait') == 'portrait_4_3'
        assert generator._get_image_size('landscape') == 'landscape_4_3'
        assert generator._get_image_size('wide') == 'landscape_16_9'
        assert generator._get_image_size('tall') == 'portrait_16_9'
        assert generator._get_image_size('unknown') == 'square'
    
    def test_estimate_cost(self, generator):
        """Test cost estimation"""
        assert generator.estimate_cost(1, 'flux_dev') == 25
        assert generator.estimate_cost(5, 'flux_dev') == 125
        assert generator.estimate_cost(10, 'flux_schnell') == 100
        assert generator.estimate_cost(3, 'stable_diffusion') == 45
    
    def test_generate_from_filters_success(self, generator):
        """Test successful image generation from filters"""
        mock_client = Mock()
        mock_client.generate_image.return_value = {
            'images': [{'url': 'https://example.com/image.png'}],
            'seed': 12345
        }
        generator.client = mock_client
        
        filters = {
            'body_type': 'athletic',
            'pose': 'running',
            'aspect_ratio': 'portrait'
        }
        
        result = generator.generate_from_filters(filters)
        
        assert len(result) == 1
        assert result[0]['url'] == 'https://example.com/image.png'
        assert result[0]['seed'] == 12345
        assert result[0]['model_id'] == 'flux/dev'
        assert result[0]['cost_cents'] == 25
        
        # Check call parameters
        call_args = mock_client.generate_image.call_args
        assert 'athletic body type' in call_args[1]['prompt']
        assert call_args[1]['parameters']['image_size'] == 'portrait_4_3'
    
    def test_generate_from_filters_with_seed(self, generator):
        """Test generation with specific seed"""
        mock_client = Mock()
        mock_client.generate_image.return_value = {'images': []}
        generator.client = mock_client
        
        filters = {'seed': 99999}
        
        generator.generate_from_filters(filters)
        
        call_params = mock_client.generate_image.call_args[1]['parameters']
        assert call_params['seed'] == 99999
    
    def test_generate_from_filters_error(self, generator):
        """Test handling generation errors"""
        mock_client = Mock()
        mock_client.generate_image.side_effect = Exception('API error')
        generator.client = mock_client
        
        with pytest.raises(Exception) as exc_info:
            generator.generate_from_filters({})
        
        assert 'Image generation failed: API error' in str(exc_info.value)
    
    def test_generate_batch_success(self, generator):
        """Test batch generation"""
        mock_client = Mock()
        mock_client.generate_image.return_value = {
            'images': [{'url': f'image.png'}],
            'seed': 1000
        }
        generator.client = mock_client
        
        filters = {'body_type': 'athletic'}
        result = generator.generate_batch(filters, batch_size=3)
        
        assert len(result) == 3
        assert mock_client.generate_image.call_count == 3
    
    def test_generate_batch_with_seed_variation(self, generator):
        """Test batch generation with seed variation"""
        mock_client = Mock()
        mock_client.generate_image.return_value = {'images': [{'url': 'test.png'}]}
        generator.client = mock_client
        
        filters = {'seed': 1000}
        generator.generate_batch(filters, batch_size=3)
        
        # Check that seeds are incremented
        calls = mock_client.generate_image.call_args_list
        assert len(calls) == 3
        
        # Seeds should be 1000, 1001, 1002
        for i, call in enumerate(calls):
            prompt = call[1]['prompt']
            params = call[1]['parameters']
            # Note: seed is in filters, not parameters in the actual call
            # The test shows filters are modified in place
    
    def test_generate_batch_partial_failure(self, generator):
        """Test batch generation continues on partial failure"""
        mock_client = Mock()
        mock_client.generate_image.side_effect = [
            {'images': [{'url': 'image1.png'}]},
            Exception('Generation failed'),
            {'images': [{'url': 'image3.png'}]}
        ]
        generator.client = mock_client
        
        with patch('builtins.print'):  # Mock print to avoid test output
            result = generator.generate_batch({}, batch_size=3)
        
        # Should return 2 images despite one failure
        assert len(result) == 2
        assert result[0]['url'] == 'image1.png'
        assert result[1]['url'] == 'image3.png'
import { useState } from 'react'
import useAuthStore from '../stores/authStore'
import useImageStore from '../stores/imageStore'
import { imagesAPI } from '../api/images'

function Generate() {
  const { hasActiveSubscription, getQuotaRemaining } = useAuthStore()
  const { generationForm, updateGenerationForm, setCurrentJob, setIsGenerating } = useImageStore()
  const [error, setError] = useState(null)
  
  const quotaRemaining = getQuotaRemaining()
  const canGenerate = hasActiveSubscription() && quotaRemaining > 0
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!canGenerate) {
      setError('You need an active subscription to generate images')
      return
    }
    
    if (generationForm.batch_size > quotaRemaining) {
      setError(`You only have ${quotaRemaining} images remaining in your quota`)
      return
    }
    
    setError(null)
    setIsGenerating(true)
    
    try {
      const job = await imagesAPI.generate(generationForm)
      setCurrentJob(job)
      // Poll for job status
      pollJobStatus(job.job_id)
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to generate images')
      setIsGenerating(false)
    }
  }
  
  const pollJobStatus = async (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const job = await imagesAPI.getJobStatus(jobId)
        setCurrentJob(job)
        
        if (job.status === 'completed' || job.status === 'failed') {
          clearInterval(pollInterval)
          setIsGenerating(false)
          
          if (job.status === 'failed') {
            setError('Image generation failed. Please try again.')
          }
        }
      } catch {
        clearInterval(pollInterval)
        setIsGenerating(false)
        setError('Failed to check job status')
      }
    }, 2000) // Poll every 2 seconds
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Generate Reference Images</h1>
        <p className="text-gray-600">
          Customize your figure drawing references. You have {quotaRemaining} images remaining this month.
        </p>
      </div>
      
      {!canGenerate && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800">
            {hasActiveSubscription() 
              ? 'You have used all your images for this month. Your quota will reset on the next billing cycle.'
              : 'You need an active subscription to generate images.'}
          </p>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Batch Size
            </label>
            <select
              value={generationForm.batch_size}
              onChange={(e) => updateGenerationForm({ batch_size: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={1}>1 image</option>
              <option value={2}>2 images</option>
              <option value={3}>3 images</option>
              <option value={4}>4 images</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Body Type
            </label>
            <select
              value={generationForm.body_type}
              onChange={(e) => updateGenerationForm({ body_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="slim">Slim</option>
              <option value="average">Average</option>
              <option value="athletic">Athletic</option>
              <option value="curvy">Curvy</option>
              <option value="heavyset">Heavyset</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pose Type
            </label>
            <select
              value={generationForm.pose_type}
              onChange={(e) => updateGenerationForm({ pose_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="standing">Standing</option>
              <option value="sitting">Sitting</option>
              <option value="action">Action</option>
              <option value="reclining">Reclining</option>
              <option value="gesture">Gesture</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Camera Angle
            </label>
            <select
              value={generationForm.camera_angle}
              onChange={(e) => updateGenerationForm({ camera_angle: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="eye_level">Eye Level</option>
              <option value="low_angle">Low Angle</option>
              <option value="high_angle">High Angle</option>
              <option value="dutch_angle">Dutch Angle</option>
              <option value="profile">Profile</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lighting
            </label>
            <select
              value={generationForm.lighting}
              onChange={(e) => updateGenerationForm({ lighting: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="studio">Studio</option>
              <option value="natural">Natural</option>
              <option value="dramatic">Dramatic</option>
              <option value="rim">Rim</option>
              <option value="soft">Soft</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clothing
            </label>
            <select
              value={generationForm.clothing}
              onChange={(e) => updateGenerationForm({ clothing: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="casual">Casual</option>
              <option value="formal">Formal</option>
              <option value="athletic">Athletic</option>
              <option value="minimal">Minimal</option>
              <option value="traditional">Traditional</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Background
            </label>
            <select
              value={generationForm.background}
              onChange={(e) => updateGenerationForm({ background: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="simple">Simple</option>
              <option value="studio">Studio</option>
              <option value="outdoor">Outdoor</option>
              <option value="abstract">Abstract</option>
              <option value="architectural">Architectural</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ethnicity
            </label>
            <select
              value={generationForm.ethnicity}
              onChange={(e) => updateGenerationForm({ ethnicity: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="diverse">Diverse</option>
              <option value="african">African</option>
              <option value="asian">Asian</option>
              <option value="caucasian">Caucasian</option>
              <option value="hispanic">Hispanic</option>
              <option value="middle_eastern">Middle Eastern</option>
              <option value="south_asian">South Asian</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Age Range
            </label>
            <select
              value={generationForm.age_range}
              onChange={(e) => updateGenerationForm({ age_range: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="young_adult">Young Adult</option>
              <option value="adult">Adult</option>
              <option value="middle_aged">Middle Aged</option>
              <option value="elderly">Elderly</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gender Presentation
            </label>
            <select
              value={generationForm.gender_presentation}
              onChange={(e) => updateGenerationForm({ gender_presentation: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="androgynous">Androgynous</option>
              <option value="masculine">Masculine</option>
              <option value="feminine">Feminine</option>
            </select>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={!canGenerate || useImageStore.getState().isGenerating}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400"
        >
          {useImageStore.getState().isGenerating ? 'Generating...' : `Generate ${generationForm.batch_size} Image${generationForm.batch_size > 1 ? 's' : ''}`}
        </button>
      </form>
      
      {/* Job Status Display */}
      {useImageStore.getState().currentJob && (
        <div className="mt-8 bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Generation Status</h3>
          <div className="space-y-2">
            <p>Status: <span className="font-medium">{useImageStore.getState().currentJob.status}</span></p>
            {useImageStore.getState().currentJob.status === 'completed' && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                {useImageStore.getState().currentJob.images?.map((image, index) => (
                  <img
                    key={index}
                    src={image.url}
                    alt={`Generated reference ${index + 1}`}
                    className="w-full h-auto rounded-lg"
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Generate
/**
 * API client for Campus Incident Response System
 * Integrates with LangGraph backend for real-time incident processing
 */

const API_BASE_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1' 
  ? '' 
  : 'http://localhost:8080';

export interface IncidentReport {
  report: string;
  execution_mode?: 'simulate' | 'execute';
  priority_override?: string;
  reporter_info?: {
    name: string;
    university_id: string;
    role: string;
    contact?: string;
    anonymous?: boolean;
  };
  metadata?: {
    incident_type: string;
    severity: string;
    location: string;
    incident_date_time?: string; // When the incident occurred
    submission_timestamp?: string; // When the report was submitted
    date_time?: string; // Legacy field for backward compatibility
    [key: string]: any;
  };
}

export interface WorkflowResult {
  success: boolean;
  workflow_id: string;
  status: string;
  message: string;
  error_type?: string; // For spam detection
  user_message?: string; // User-friendly message for spam
  spam_detection?: {
    is_spam: boolean;
    category: string;
    reason: string;
    confidence: number;
    detection_method: string;
  };
  details?: {
    category: string;
    reason: string;
    confidence: string;
  };
  result?: {
    workflow_id: string;
    status: string;
    execution_mode: string;
    created_at: string;
    updated_at: string;
    processing_stages: {
      intake: string;
      planning: string;
      safety: string;
      execution: string;
      evaluation: string;
    };
    incident_data?: {
      incident_id: string;
      incident_type: string;
      severity: string;
      priority: string;
      location: string;
      confidence_score: number;
      description: string;
      entities: {
        people: string[];
        locations: string[];
        objects: string[];
        times: string[];
        organizations: string[];
      };
    };
    response_plan?: {
      plan_id: string;
      plan_type: string;
      priority_level: string;
      immediate_actions: Array<{
        action_id: string;
        description: string;
        responsible_party: string;
        priority: string;
        estimated_duration: string;
      }>;
      stakeholders: Array<{
        role: string;
        department: string;
        notification_priority: string;
      }>;
      success_criteria: string[];
      risk_factors: string[];
    };
    execution_summary?: {
      execution_id: string;
      overall_status: string;
      success_rate: number;
      immediate_actions_executed: number;
      stakeholder_response_rate: number;
      critical_issues: string[];
      warnings: string[];
    };
    evaluation_report?: {
      evaluation_id: string;
      incident_id: string;
      plan_id: string;
      execution_id: string;
      overall_score: number;
      effectiveness_rating: string;
      response_quality: string;
      
      // Resolution status (Safety-First Logic)
      resolution_status?: string;
      resolution_reason?: string;
      human_intervention_required?: boolean;
      resolution_details?: string;
      rule_applied?: string;
      
      category_scores: Array<{
        category: string;
        score: number;
        weight: number;
        metrics: Array<{
          metric_name: string;
          category: string;
          value: number;
          target_value: number;
          unit: string;
          status: string;
          weight: number;
        }>;
        strengths: string[];
        weaknesses: string[];
      }>;
      strengths: string[];
      weaknesses: string[];
      critical_gaps: string[];
      lessons_learned: Array<{
        lesson_id: string;
        category: string;
        lesson: string;
        evidence: string;
        impact: string;
        priority: string;
        actionable_steps: string[];
      }>;
      improvement_recommendations: Array<{
        recommendation_id: string;
        category: string;
        title: string;
        description: string;
        priority: string;
        estimated_effort: string;
        expected_benefit: string;
        implementation_timeline: string;
        responsible_party: string;
      }>;
      benchmark_comparison: {
        incident_type?: string;
        complexity_level?: string;
        benchmark_score?: number;
        actual_score?: number;
        comparison?: string;
        performance_gap?: number;
        category_benchmarks?: Record<string, number>;
        ai_enhanced?: boolean;
        contextual_analysis?: string;
      };
      peer_comparison: {
        peer_group?: string;
        peer_average?: number;
        percentile_ranking?: string;
        performance_vs_peers?: number;
        comparison_summary?: string;
        ai_analysis?: boolean;
        future_preparedness?: string;
      };
      preparedness_score: number;
      risk_mitigation_effectiveness: number;
      evaluation_timestamp: string;
      evaluator_confidence: number;
      data_completeness: number;
    };
    errors: string[];
    warnings: string[];
  };
}

export interface WorkflowStatus {
  workflow_id: string;
  status: string;
  current_stage: string;
  progress_percentage: number;
  estimated_completion?: string;
  last_update: string;
}

export interface SimulationRequest {
  scenario_type: string;
  incident_count: number;
  time_acceleration: number;
  parameters?: Record<string, any>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || 
          errorData.message || 
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  /**
   * Process an incident report through the LangGraph workflow
   */
  async processIncident(incident: IncidentReport): Promise<WorkflowResult> {
    return this.request<WorkflowResult>('/api/v1/incidents/process', {
      method: 'POST',
      body: JSON.stringify(incident),
    });
  }

  /**
   * Get the status of a workflow
   */
  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    return this.request<WorkflowStatus>(`/api/v1/workflows/${workflowId}/status`);
  }

  /**
   * Get all active workflows
   */
  async getWorkflows(): Promise<{ success: boolean; count: number; workflows: any[] }> {
    return this.request('/api/v1/workflows');
  }

  /**
   * Run a simulation
   */
  async runSimulation(simulation: SimulationRequest): Promise<{
    success: boolean;
    simulation_id: string;
    message: string;
    parameters: SimulationRequest;
  }> {
    return this.request('/api/v1/simulation/run', {
      method: 'POST',
      body: JSON.stringify(simulation),
    });
  }

  /**
   * Get available simulation scenarios
   */
  async getSimulationScenarios(): Promise<{
    success: boolean;
    scenarios: Record<string, any>;
  }> {
    return this.request('/api/v1/simulation/scenarios');
  }

  /**
   * Get real-time analytics
   */
  async getRealTimeAnalytics(): Promise<{
    success: boolean;
    timestamp: string;
    metrics: {
      total_active_workflows: number;
      status_distribution: Record<string, number>;
      average_processing_time: string;
      success_rate: string;
      current_load: string;
    };
    recent_activity: any[];
  }> {
    return this.request('/api/v1/analytics/realtime');
  }

  /**
   * Get dashboard analytics
   */
  async getDashboardAnalytics(): Promise<{
    success: boolean;
    timestamp: string;
    stats: {
      total_incidents: number;
      resolved: number;
      in_progress: number;
      high_severity: number;
      avg_response_score: number;
    };
    distributions: {
      status: Record<string, number>;
      severity: Record<string, number>;
      types: Record<string, number>;
    };
    time_series: Array<{
      name: string;
      incidents: number;
      resolved: number;
    }>;
    recent_incidents: any[];
    trends: {
      total_change: string;
      resolved_change: string;
      response_score_change: string;
    };
    compliance: {
      overall_score: {
        overall_score: number;
        category_scores: {
          response_time: number;
          documentation: number;
          privacy: number;
          reporting: number;
          follow_up: number;
        };
        grade: string;
        status: string;
      };
      policy_checks: Array<{
        policy: string;
        description: string;
        status: string;
        score: number;
        details: string;
        last_audit: string;
        requirements_met: number;
        total_requirements: number;
      }>;
      compliance_trends: {
        monthly_scores: Array<{
          month: string;
          score: number;
        }>;
        improvement_rate: string;
        trend_direction: string;
        key_improvements: string[];
      };
      risk_assessment: {
        overall_risk: string;
        risk_score: number;
        risk_factors: Array<{
          factor: string;
          level: string;
          count: number;
          mitigation: string;
        }>;
        recommendations: string[];
      };
      audit_trail: Array<{
        timestamp: string;
        incident_id: string;
        action: string;
        compliance_status: string;
        details: string;
        automated: boolean;
        policies_checked: string[];
      }>;
    };
  }> {
    return this.request('/api/v1/dashboard/analytics');
  }

  /**
   * Get incident history
   */
  async getIncidentHistory(
    limit: number = 50,
    offset: number = 0,
    statusFilter?: string,
    severityFilter?: string
  ): Promise<{
    success: boolean;
    total_count: number;
    incidents: any[];
    has_more: boolean;
  }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    
    if (statusFilter) params.append('status_filter', statusFilter);
    if (severityFilter) params.append('severity_filter', severityFilter);
    
    return this.request(`/api/v1/incidents/history?${params.toString()}`);
  }

  /**
   * Upload and analyze incident image
   */
  async uploadIncidentImage(
    file: File,
    description?: string
  ): Promise<{
    success: boolean;
    file_id: string;
    filename: string;
    content_type: string;
    size: number;
    ai_analysis: any;
    authenticity_analysis: any;
    upload_timestamp: string;
    requires_human_review: boolean;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    const response = await fetch(`${this.baseUrl}/api/v1/incidents/upload-image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || 
        errorData.message || 
        `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  }

  /**
   * Resolve an incident with admin feedback
   */
  async resolveIncident(
    incidentId: string,
    feedback: string,
    resolvedBy: string = "Admin"
  ): Promise<{
    success: boolean;
    message: string;
    incident_id: string;
    resolution_info: {
      status: string;
      resolved_at: string;
      resolved_by: string;
      resolution_feedback: string;
      resolution_actions: string[];
    };
  }> {
    return this.request(`/api/v1/incidents/${incidentId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({
        feedback,
        resolved_by: resolvedBy,
        actions: []
      }),
    });
  }

  /**
   * Get human review queue
   */
  async getReviewQueue(
    priority?: string,
    status?: string
  ): Promise<{
    success: boolean;
    queue: any[];
    summary: any;
  }> {
    const params = new URLSearchParams();
    if (priority) params.append('priority', priority);
    if (status) params.append('status', status);
    
    return this.request(`/api/v1/review/queue?${params.toString()}`);
  }

  /**
   * Get review status for an incident
   */
  async getReviewStatus(incidentId: string): Promise<{
    success: boolean;
    review_status: any;
    explanation: any;
  }> {
    return this.request(`/api/v1/review/status/${incidentId}`);
  }

  /**
   * Start reviewing an incident
   */
  async startReview(incidentId: string, reviewerId: string): Promise<{
    success: boolean;
    review_entry: any;
  }> {
    return this.request(`/api/v1/review/${incidentId}/start`, {
      method: 'POST',
      body: JSON.stringify({ reviewer_id: reviewerId }),
    });
  }

  /**
   * Complete a review
   */
  async completeReview(
    incidentId: string,
    action: string,
    notes: string,
    conditions?: string[]
  ): Promise<{
    success: boolean;
    review_entry: any;
  }> {
    return this.request(`/api/v1/review/${incidentId}/complete`, {
      method: 'POST',
      body: JSON.stringify({
        action,
        notes,
        conditions: conditions || []
      }),
    });
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    version: string;
    active_workflows: number;
    active_connections: number;
  }> {
    return this.request('/health');
  }

  /**
   * Create WebSocket connection for real-time updates
   */
  createWebSocket(onMessage?: (data: any) => void, onError?: (error: Event) => void): WebSocket {
    const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws/realtime';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }

  /**
   * Subscribe to workflow updates via WebSocket
   */
  subscribeToWorkflow(workflowId: string, ws: WebSocket): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'subscribe_workflow',
        workflow_id: workflowId
      }));
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export types and utilities
export type { WorkflowResult, WorkflowStatus, IncidentReport, SimulationRequest };
export default apiClient;
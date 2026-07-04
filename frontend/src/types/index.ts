/** Agent types available in the NAP system */
export type AgentType =
  | "architect"
  | "backend"
  | "frontend"
  | "documentation"
  | "reviewer";

/** Status of an agent execution */
export type AgentStatus = "queued" | "running" | "completed" | "failed";

/** Request to execute an agent */
export interface AgentRequest {
  agent_type: AgentType;
  task: string;
  context?: Record<string, unknown>;
}

/** Response from an agent execution */
export interface AgentResponse {
  agent_type: AgentType;
  status: AgentStatus;
  result: Record<string, unknown>;
  artifacts: string[];
}

/** Project representation */
export interface Project {
  id: number;
  name: string;
  description?: string;
  status: "draft" | "active" | "completed" | "archived";
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

/** Health check response */
export interface HealthCheck {
  status: string;
  service: string;
  version: string;
}
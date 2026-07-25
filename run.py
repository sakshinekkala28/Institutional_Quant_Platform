from orchestration.master_orchestrator import MasterOrchestrator

orch = MasterOrchestrator()

orch.initialize()

print(orch.pipeline_summary())
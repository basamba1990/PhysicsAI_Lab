import { z } from "zod";
import { protectedProcedure, router } from "../_core/trpc";
import {
  createSimulation,
  getSimulation,
  getUserSimulations,
  updateSimulationStatus,
  cachePrediction,
  getPrediction,
  registerModelVersion,
  getLatestModelVersion,
  listModelVersions,
  logEthicsValidation,
  getEthicsLogs,
  createTrainingJob,
  getUserTrainingJobs,
  updateTrainingJobProgress,
  completeTrainingJob,
} from "../physics_db";

export const simulationsRouter = router({
  // Create a new simulation
  create: protectedProcedure
    .input(
      z.object({
        name: z.string().min(1),
        description: z.string().optional(),
        parameters: z.record(z.any()),
      })
    )
    .mutation(async ({ ctx, input }) => {
      return await createSimulation({
        userId: ctx.user.id,
        name: input.name,
        description: input.description,
        parameters: input.parameters,
        status: "pending",
      });
    }),

  // Get user's simulations
  list: protectedProcedure.query(async ({ ctx }) => {
    return await getUserSimulations(ctx.user.id);
  }),

  // Get single simulation
  get: protectedProcedure
    .input(z.object({ id: z.number() }))
    .query(async ({ input }) => {
      return await getSimulation(input.id);
    }),

  // Update simulation status
  updateStatus: protectedProcedure
    .input(z.object({ id: z.number(), status: z.string() }))
    .mutation(async ({ input }) => {
      await updateSimulationStatus(input.id, input.status);
      return { success: true };
    }),

  // Cache prediction
  cachePrediction: protectedProcedure
    .input(
      z.object({
        inputParams: z.record(z.any()),
        predictionMean: z.record(z.any()),
        predictionStd: z.record(z.any()).optional(),
        modelVersion: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      return await cachePrediction({
        inputParams: input.inputParams,
        predictionMean: input.predictionMean,
        predictionStd: input.predictionStd,
        modelVersion: input.modelVersion,
      });
    }),

  // Get cached prediction
  getPrediction: protectedProcedure
    .input(z.object({ inputParams: z.record(z.any()) }))
    .query(async ({ input }) => {
      return await getPrediction(input.inputParams);
    }),
});

export const modelsRouter = router({
  // Register model version
  registerVersion: protectedProcedure
    .input(
      z.object({
        modelId: z.string(),
        version: z.string(),
        modelPath: z.string(),
        onnxPath: z.string().optional(),
        config: z.record(z.any()).optional(),
        metrics: z.record(z.any()).optional(),
        trainingDataHash: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      return await registerModelVersion({
        modelId: input.modelId,
        version: input.version,
        modelPath: input.modelPath,
        onnxPath: input.onnxPath,
        config: input.config,
        metrics: input.metrics,
        trainingDataHash: input.trainingDataHash,
      });
    }),

  // Get latest model version
  getLatest: protectedProcedure
    .input(z.object({ modelId: z.string() }))
    .query(async ({ input }) => {
      return await getLatestModelVersion(input.modelId);
    }),

  // List all versions of a model
  listVersions: protectedProcedure
    .input(z.object({ modelId: z.string() }))
    .query(async ({ input }) => {
      return await listModelVersions(input.modelId);
    }),
});

export const ethicsRouter = router({
  // Log ethics validation
  logValidation: protectedProcedure
    .input(
      z.object({
        simulationId: z.number(),
        violations: z.array(z.any()).optional(),
        ethicsScore: z.number().optional(),
        isEthical: z.boolean().optional(),
      })
    )
    .mutation(async ({ input }) => {
      return await logEthicsValidation({
        simulationId: input.simulationId,
        violations: input.violations,
        ethicsScore: input.ethicsScore,
        isEthical: input.isEthical,
      });
    }),

  // Get ethics logs for simulation
  getLogs: protectedProcedure
    .input(z.object({ simulationId: z.number() }))
    .query(async ({ input }) => {
      return await getEthicsLogs(input.simulationId);
    }),
});

export const trainingRouter = router({
  // Create training job
  create: protectedProcedure
    .input(
      z.object({
        modelId: z.string(),
        datasetPath: z.string().optional(),
        config: z.record(z.any()).optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      return await createTrainingJob({
        userId: ctx.user.id,
        modelId: input.modelId,
        datasetPath: input.datasetPath,
        config: input.config ? JSON.stringify(input.config) : undefined,
        status: "pending",
      });
    }),

  // List user's training jobs
  list: protectedProcedure.query(async ({ ctx }) => {
    return await getUserTrainingJobs(ctx.user.id);
  }),

  // Update training progress
  updateProgress: protectedProcedure
    .input(
      z.object({
        jobId: z.number(),
        progress: z.number(),
        metrics: z.record(z.any()).optional(),
      })
    )
    .mutation(async ({ input }) => {
      await updateTrainingJobProgress(input.jobId, input.progress, input.metrics);
      return { success: true };
    }),

  // Complete training job
  complete: protectedProcedure
    .input(z.object({ jobId: z.number(), metrics: z.record(z.any()) }))
    .mutation(async ({ input }) => {
      await completeTrainingJob(input.jobId, input.metrics);
      return { success: true };
    }),
});

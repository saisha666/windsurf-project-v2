# Post-training analysis script
library(tidyverse)
library(caret)

# Load results
results <- fromJSON("training_results.json")

# Create performance plots
pdf("training_performance.pdf")

# Plot resource usage
plot(results$ubuntu_resources$cpu, type="l", col="blue", 
     main="System Resource Usage", xlab="Time", ylab="CPU %")
lines(results$windows_resources$cpu, col="red")
legend("topright", legend=c("Ubuntu", "Windows"), col=c("blue", "red"), lty=1)

# Plot model metrics if available
if (!is.null(results$model_metrics)) {
  plot(results$model_metrics$accuracy, type="l", 
       main="Model Performance", xlab="Iteration", ylab="Accuracy")
}

dev.off()

# Print summary
cat("\nTraining Summary:\n")
cat("Model Type:", results$training_config$model_type, "\n")
cat("Iterations:", results$training_config$iterations, "\n")
cat("Learning Rate:", results$training_config$learning_rate, "\n")

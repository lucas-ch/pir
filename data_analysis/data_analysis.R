# Installer les bibliothèques si nécessaire
if (!require(jsonlite)) install.packages("jsonlite")
if (!require(dplyr)) install.packages("dplyr")
if (!require(gridExtra)) install.packages("gridExtra")
if (!require(cowplot)) install.packages("cowplot")
if (!require(grid)) install.packages("grid")
if (!require(patchwork)) install.packages("patchwork")

# Charger les bibliothèques
library(jsonlite)
library(dplyr)
library(ggplot2)
library(gridExtra)
library(grid)
library(cowplot)
library(patchwork)

# Importer le fichier JSON
file_path <- "result.txt"
data <- fromJSON(file_path)

# Filtrer les objets avec assignement_method = "DIAS" et random_init = FALSE
filtered_data <- data %>%
  filter(assignement_method == "DIAS" & random_init == FALSE)

# Ajouter la colonne communication_number au calcul des différences
filtered_data <- filtered_data %>%
  rowwise() %>%
  mutate(
    diff_utility = (tail(unlist(result$total_utility_evolution), 1) - result$ssi_init_utility) / result$ssi_init_utility * 100,
    diff_distance = (tail(unlist(result$total_distance_evolution), 1) - result$ssi_init_distance) / result$ssi_init_distance * 100,
    diff_time = (tail(unlist(result$planned_time_evolution), 1) - result$ssi_init_planned_time) / result$ssi_init_planned_time * 100,
    communication_number = ((communication_number - 27)/27) * 100  # On garde la valeur de communication_number telle quelle
  ) %>%
  ungroup()


create_percentage_plot <- function(data, metric, metric_name, reward, binwidth = NULL, x_breaks = NULL) {
  metric_data <- data %>% filter(reward_factor == reward) %>% pull(metric)
  
  # Binwidth automatique si non spécifié
  if (is.null(binwidth)) {
    range_val <- max(metric_data, na.rm = TRUE) - min(metric_data, na.rm = TRUE)
    binwidth <- max(range_val / 30, 1)
  }
  
  # Breaks automatiques si non spécifiés
  if (is.null(x_breaks)) {
    min_val <- floor(min(metric_data, na.rm = TRUE) / 10) * 10
    max_val <- ceiling(max(metric_data, na.rm = TRUE) / 10) * 10
    x_breaks <- seq(min_val, max_val, by = 10)
  }
  
  ggplot(data %>% filter(reward_factor == reward), 
         aes_string(x = metric, fill = "as.factor(reward_factor)")) +
    geom_histogram(aes(y = ..count.. / sum(..count..) * 100),
                   binwidth = binwidth, color = "black", alpha = 0.7) +
    scale_fill_manual(
      values = c("0.95" = "#d62728", "1" = "#1f77b4"),
      name = "\u03B1",
      labels = c("0.95" = "0.95", "1" = "1")
    ) +
    labs(
      y = "",
      x = paste("", metric_name, "(%)"),
    ) +
    scale_x_continuous(breaks = x_breaks) +
    scale_y_continuous(breaks = seq(0, 100, by = 10), limits = c(0, 100)) +
    theme_minimal() +
    theme(
      legend.position = "right",
      panel.grid.major = element_line(colour = "grey90", linewidth = 0.2),
      panel.grid.minor = element_blank()
    )
}

# Création des graphiques
plot_utility_1 <- create_percentage_plot(filtered_data, "diff_utility", "Utilité totale", 1, binwidth = 1, x_breaks = seq(-20, 40, by = 1))
plot_utility_095 <- create_percentage_plot(filtered_data, "diff_utility", "Utilité totale", 0.95, binwidth = 2, x_breaks = seq(-20, 40, by = 2))
plot_distance_1 <- create_percentage_plot(filtered_data, "diff_distance", "Distance totale", 1, binwidth = 2.5, x_breaks = seq(-20, 40, by = 5))
plot_distance_095 <- create_percentage_plot(filtered_data, "diff_distance", "Distance totale", 0.95, binwidth = 4, x_breaks = seq(-20, 40, by = 5))
plot_time_1 <- create_percentage_plot(filtered_data, "diff_time", "Temps de mission", 1, binwidth = 5,x_breaks = seq(-40, 40, by = 20))
plot_time_095 <- create_percentage_plot(filtered_data, "diff_time", "Temps de mission", 0.95, binwidth = 5, x_breaks = seq(-40, 40, by = 20))
plot_communication_1 <- create_percentage_plot(filtered_data, "communication_number", "Nombre de communications", 1, binwidth = 10, x_breaks = seq(0, 200, by = 20))
plot_communication_095 <- create_percentage_plot(filtered_data, "communication_number", "Nombre de communications", 0.95, binwidth = 10, x_breaks = seq(0, 300, by = 20))


# Organisation finale en grille avec légende partagée
final_plot <- (plot_utility_1 + plot_utility_095) /
  (plot_distance_1 + plot_distance_095) /
  (plot_time_1 + plot_time_095) /
  plot_layout(guides = "collect") & theme(legend.position = 'bottom')

# Affichage du graphique final
final_plot


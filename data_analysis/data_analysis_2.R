library(jsonlite)
library(dplyr)
library(ggplot2)
library(tidyr)

### Chargement et extraction des données ###
# Chemin du fichier
file_path <- "result.txt"

# Lire les données depuis le fichier JSON en désactivant la simplification automatique
data <- fromJSON(file_path, simplifyDataFrame = FALSE)

# Si 'data' n'est pas déjà une liste, on le transforme en liste
if (!is.list(data)) {
  data <- list(data)
}

# Filtrer les données : garder uniquement les objets où random_init est FALSE
data_filtered <- Filter(function(x) {
  is.list(x) && !is.null(x$random_init) && x$random_init == FALSE
}, data)

# Extraire les colonnes simples (id, communication_number, reward_factor)
df <- data.frame(
  id = sapply(data_filtered, function(x) x$id),
  communication_number = sapply(data_filtered, function(x) x$communication_number),
  reward_factor = sapply(data_filtered, function(x) x$reward_factor),
  stringsAsFactors = FALSE
)

# Extraire les données imbriquées dans 'result'
result_data <- do.call(rbind, lapply(data_filtered, function(x) {
  res <- x$result
  data.frame(
    ssi_init_utility       = res$ssi_init_utility,
    ssi_init_distance      = res$ssi_init_distance,
    ssi_init_planned_time  = res$ssi_init_planned_time,
    last_total_utility     = tail(res$total_utility_evolution, 1),
    last_total_distance    = tail(res$total_distance_evolution, 1),
    last_total_planned_time = tail(res$planned_time_evolution, 1),
    planned_time_length    = length(res$planned_time_evolution),
    stringsAsFactors = FALSE
  )
}))

# Combiner les deux data frames
data_extracted <- cbind(df, result_data)

### Figure 1 : Comparaison de Distance et Temps pour reward_factor = 1 et 0.95 ###
# On travaille sur les colonnes de distance et temps (planned_time)
data_long_dt <- data_extracted %>%
  pivot_longer(
    cols = c(ssi_init_distance, last_total_distance, 
             ssi_init_planned_time, last_total_planned_time),
    names_to = c("source", "measure"),
    names_pattern = "(ssi_init|last_total)_(.*)",
    values_to = "value"
  )

# Créer une colonne 'group' pour combiner source et reward_factor
data_long_dt <- data_long_dt %>%
  mutate(group = factor(paste(source, reward_factor, sep = "_"),
                        levels = c("ssi_init_1", "last_total_1", 
                                   "ssi_init_0.95", "last_total_0.95")))

# Création du graphique (figure 1) avec des couleurs personnalisées et labels modifiés
p1 <- ggplot(data_long_dt, aes(x = group, y = value, fill = group)) +
  geom_boxplot() +
  # Ajouter la médiane en point et en texte (en noir)
  stat_summary(fun = median, geom = "point", size = 3, color = "black") +
  stat_summary(fun = median, geom = "text", aes(label = sprintf('%.1f', ..y..)),
               vjust = -0.5, color = "black") +
  scale_fill_manual(values = c(
    "ssi_init_1" = "#1f77b4",      # Bleu foncé
    "last_total_1" = "#87cdeb",    # Bleu clair/transparent
    "ssi_init_0.95" = "#d62728",   # Rouge foncé
    "last_total_0.95" = "#f28e8e"  # Rouge clair/transparent
  )) +
  scale_x_discrete(labels = c(
    "ssi_init_1" = "EUT (\u03B1 = 1)",
    "last_total_1" = "ED (\u03B1 = 1)",
    "ssi_init_0.95" = "EUT (\u03B1 = 0.95)",
    "last_total_0.95" = "ED (\u03B1 = 0.95)"
  )) +
  facet_wrap(~ measure, scales = "free", 
             labeller = labeller(measure = c("distance" = "Distance totale (cases)", 
                                             "planned_time" = "Temps de mission (s)"))) +
  labs(title = "",
       x = "",
       y = "") +
  theme_minimal() +
  theme(legend.position = "none")

print(p1)

### Figure 2 : Utilité pour reward_factor = 1 ###
# Filtrer pour reward_factor == 1 et travailler sur les colonnes d'utilité
data_long_util_1 <- data_extracted %>%
  filter(reward_factor == 1) %>%
  pivot_longer(
    cols = c(ssi_init_utility, last_total_utility),
    names_to = "source",
    names_pattern = "(ssi_init|last_total)_utility",
    values_to = "value"
  )
data_long_util_1$source <- factor(data_long_util_1$source, levels = c("ssi_init", "last_total"))

p2 <- ggplot(data_long_util_1, aes(x = source, y = value, fill = source)) +
  geom_boxplot() +
  stat_summary(fun = median, geom = "point", size = 3, color = "black") +
  stat_summary(fun = median, geom = "text",
               aes(label = sprintf('%.1f', ..y..)),
               vjust = -0.5, color = "black") +
  scale_fill_manual(values = c(
    "ssi_init" = "#1f77b4",  # Bleu foncé
    "last_total" = "#87cdeb" # Bleu clair/transparent
  )) +
  scale_x_discrete(labels = c(
    "ssi_init" = "EUT",
    "last_total" = "ED"
  )) +
  labs(title = "",
       x = "",
       y = "Utilité") +
  theme_minimal() +
  theme(legend.position = "none")

print(p2)

### Figure 3 : Utilité pour reward_factor = 0.95 ###
data_long_util_095 <- data_extracted %>%
  filter(reward_factor == 0.95) %>%
  pivot_longer(
    cols = c(ssi_init_utility, last_total_utility),
    names_to = "source",
    names_pattern = "(ssi_init|last_total)_utility",
    values_to = "value"
  )
data_long_util_095$source <- factor(data_long_util_095$source, levels = c("ssi_init", "last_total"))

p3 <- ggplot(data_long_util_095, aes(x = source, y = value, fill = source)) +
  geom_boxplot() +
  stat_summary(fun = median, geom = "point", size = 3, color = "black") +
  stat_summary(fun = median, geom = "text",
               aes(label = sprintf('%.1f', ..y..)),
               vjust = -0.5, color = "black") +
  scale_fill_manual(values = c(
    "ssi_init" = "#d62728",  # Rouge foncé
    "last_total" = "#f28e8e" # Rouge clair/transparent
  )) +
  scale_x_discrete(labels = c(
    "ssi_init" = "EUT",
    "last_total" = "ED"
  )) +
  labs(title = "",
       x = "",
       y = "Utilité") +
  theme_minimal() +
  theme(legend.position = "none")

print(p3)

### Calcul des écarts-types de last_total_utility par reward_factor ###
std_devs <- data_extracted %>%
  group_by(reward_factor) %>%
  summarize(std_dev_utility = sd(last_total_planned_time, na.rm = TRUE))

print(std_devs)


# Shared setup sourced (silently) at the top of every chapter.
# Students do not need this file to run the examples; it only sets the
# random seed and the plot styling used in the rendered book.

set.seed(7273)

options(digits = 4, pillar.sigfig = 4, width = 90)

# format p-values for inline text
fmt_p <- function(p) {
  if (p < 0.001) "less than 0.001" else format(round(p, 3), nsmall = 3)
}

# UTSA colors for ggplot2 -------------------------------------------------
if (requireNamespace("ggplot2", quietly = TRUE) &&
    requireNamespace("sparkscolors", quietly = TRUE)) {
  library(ggplot2)
  midnight <- sparkscolors::utsa_cols("midnight")
  orange <- sparkscolors::utsa_cols("orange")

  ggplot2::theme_set(
    ggplot2::theme_minimal(base_size = 12) +
      ggplot2::theme(
        text = ggplot2::element_text(colour = midnight),
        axis.text = ggplot2::element_text(colour = midnight),
        panel.grid.minor = ggplot2::element_blank(),
        plot.title = ggplot2::element_text(face = "bold")
      )
  )

  options(
    ggplot2.discrete.colour = function(...) sparkscolors::scale_colour_utsa(...),
    ggplot2.discrete.fill = function(...) sparkscolors::scale_fill_utsa(...),
    ggplot2.continuous.colour = function(...) sparkscolors::scale_colour_utsa(discrete = FALSE, ...),
    ggplot2.continuous.fill = function(...) sparkscolors::scale_fill_utsa(discrete = FALSE, ...)
  )

  ggplot2::update_geom_defaults("point", list(colour = midnight))
  ggplot2::update_geom_defaults("bar", list(fill = midnight, colour = "white"))
  ggplot2::update_geom_defaults("boxplot", list(colour = midnight, fill = "#C8DCFF"))
  ggplot2::update_geom_defaults("line", list(colour = midnight))
  ggplot2::update_geom_defaults("path", list(colour = midnight))
  ggplot2::update_geom_defaults("smooth", list(colour = orange, fill = "#D5CFC8"))
  ggplot2::update_geom_defaults("errorbar", list(colour = midnight))
}

# UTSA colors for base R graphics: col = 1 is Midnight, col = 2 is Orange
grDevices::palette(c("#032044", "#F15A22", "#265BF7", "#A06620",
                     "#DBB485", "#C8DCFF", "#D5CFC8"))

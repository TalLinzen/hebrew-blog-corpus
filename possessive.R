library(plotrix)
library(Hmisc)
library(Design)
library(lme4)
library(tikzDevice)

cutoff <- c(13, 17, 19, 22, 27, 36, 61)
binlabels <- paste(cutoff[1:(length(cutoff)-1)], cutoff[2:length(cutoff)] - 1, sep='-')
figures_dir <- '/home/tal/Dropbox/naples/figures/'

d <- read.csv('data/r_data.csv')
d$type <- factor(d$type)
d$sex <- factor(d$sex)
d$verb <- factor(d$verb)
d$agecat <- cut(d$age, cutoff, labels=binlabels, right=TRUE)

ddist <- datadist(d)
options(datadist="ddist")

plot_by_age <- function(l, color) {
    ci <- tapply(l$type == "pd", l$agecat, function (x) (binconf(sum(x), length(x))))
    ci <- do.call(rbind, ci)
    plotCI(x=1:(length(cutoff)-1), y=ci[,1], li=ci[,2], ui=ci[,3], xaxt="n", ylim=c(0.3,1), ylab="Frequency of PD", xlab="Age group", col=color)
    line <- lm(ci[,1] ~ seq(1, length(cutoff) - 1))
    abline(line$coef, col=color, lty=2)
}

possessive_by_age <- function() {
    tikz(paste(figures_dir, "PossessiveByAge.tex", sep=''), width=4, height=3)
    par(cex=0.75, las=1)
    bp_col <- "blue"
    non_bp_col <- "darkgreen" 
    plot_by_age(d[d$bp,], bp_col)
    par(new=TRUE)
    plot_by_age(d[!d$bp,], non_bp_col)
    legend("topleft", c("Body part", "Other"), inset=0.01, fill=c(bp_col, non_bp_col), title="Type of possessum:")
    title("Association between body part possessums and PD")
    axis(1, at=1:(length(cutoff)-1), labels=binlabels)
    dev.off()
}

plot_gender_age_bars <- function() {
    tikz(paste(figures_dir, "GenderAgeBars.tex", sep=''), width=4, height=3)
    par(cex=0.75, las=1)
    t <- table(d$sex, d$agecat) 
    barplot(t, col=c("darkblue", "red"), legend=rownames(t), main="Number of possessive sentences by age and gender")
    dev.off()
}    

# lrm(type ~ age + sex, data=d)
# l <- lmer(type ~ agecat * bp + (1 | verb), family=binomial, data=d)
# l <- lmer(type ~ agecat * bp + sex * bp + (bp | verb) + (1 | user), family=binomial, data=d)

library(plotrix)
library(Hmisc)
library(Design)
library(lme4)

cutoff <- c(13, 17, 20, 27, 36, 61)

d <- read.csv('data/r_data.csv')
d$type <- factor(d$type)
d$sex <- factor(d$sex)
d$verb <- factor(d$verb)
d$agecat <- cut(d$age, cutoff)

ddist <- datadist(d)
options(datadist="ddist")

plot_by_age <- function(l, color) {
    ci <- tapply(l$type == "pd", l$agecat, function (x) (binconf(sum(x), length(x))))
    ci <- do.call(rbind, ci)
    xlabels <- paste(cutoff[1:(length(cutoff)-1)], cutoff[2:length(cutoff)], sep='-')
    plotCI(x=1:(length(cutoff)-1), y=ci[,1], li=ci[,2], ui=ci[,3], xaxt="n", ylim=c(0.3,1), ylab="Frequency of PD", xlab="Age group", col=color)
    axis(1, at=1:(length(cutoff)-1), labels=xlabels)
}

possessive_by_age <- function() {
    bp_col <- "blue"
    non_bp_col <- "darkgreen" 
    plot_by_age(d[d$bp,], bp_col)
    par(new=TRUE)
    plot_by_age(d[!d$bp,], non_bp_col)
    legend("topleft", c("Body part", "Other"), inset=0.05, fill=c(bp_col, non_bp_col), title="Type of possessum:")
    title("Association between body part possessums and PD")
}

# lrm(type ~ age + sex, data=d)
# l <- lmer(type ~ agecat * bp + (1 | verb), family=binomial, data=d)
# l <- lmer(type ~ agecat * bp + sex * bp + (bp | verb) + (1 | user), family=binomial, data=d)

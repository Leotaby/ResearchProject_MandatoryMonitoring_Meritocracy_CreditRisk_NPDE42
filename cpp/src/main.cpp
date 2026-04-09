#include <cmath>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>

static double sigmoid(double x) { return 1.0/(1.0+std::exp(-x)); }

int main() {
    constexpr int N=5000, T=9, Y0=2015;
    std::mt19937_64 rng(42);
    std::normal_distribution<> n01(0,1);
    std::uniform_real_distribution<> u01(0,1);
    auto beta=[&](double a,double b){
        std::gamma_distribution<> ga(a,1),gb(b,1);
        double x=ga(rng),y=gb(rng); return x/(x+y);
    };

    struct F { double base,gr,fe,mq,bd; int fam; double gov=0; };
    std::vector<F> firms(N);
    for(auto&f:firms){
        f.base=14.0+0.6*n01(rng); f.gr=0.03+0.02*n01(rng);
        f.fam=u01(rng)<0.55?1:0; f.bd=beta(2,5);
        f.mq=n01(rng); f.fe=0.4*n01(rng);
    }

    std::system("mkdir -p ../output");
    std::ofstream out("../output/sim_panel.csv");
    out<<"firm_id,year,threshold,log_assets,running,auditor,governance,"
         "meritocracy,productivity,leverage,interest_rate,default_risk,distressed\n";

    for(int t=0;t<T;t++){
        int yr=Y0+t;
        double thr=yr<=2018?14.0:13.8;
        for(int i=0;i<N;i++){
            auto&f=firms[i];
            double la=f.base+f.gr*t+0.15*n01(rng);
            double run=la-thr;
            double pa=std::clamp(0.1+0.75*sigmoid(4*run),0.02,0.98);
            int aud=u01(rng)<pa?1:0;
            f.gov=0.6*f.gov+0.85*aud-0.45*f.fam+0.1*f.mq+0.2*f.fe+0.6*n01(rng);
            double mer=0.55*f.gov-0.35*f.fam+0.2*f.mq+0.7*n01(rng);
            double prod=std::exp(2+0.22*mer+0.05*f.gov+0.2*f.fe+0.25*n01(rng));
            double lev=std::clamp(0.35+0.1*f.bd-0.03*f.gov+0.08*n01(rng),0.05,0.95);
            double ir=std::clamp(0.045-0.0045*f.gov-0.003*mer+0.03*lev+0.007*f.bd+0.006*n01(rng),0.005,0.25);
            double dr=sigmoid(-3.2+2.2*lev+7.5*ir-0.35*f.gov-0.1*std::log(prod)+0.4*n01(rng));
            int dis=u01(rng)<std::clamp(dr,0.001,0.999)?1:0;
            out<<i+1<<","<<yr<<","<<thr<<","<<la<<","<<run<<","<<aud<<","
               <<f.gov<<","<<mer<<","<<prod<<","<<lev<<","<<ir<<","<<dr<<","<<dis<<"\n";
        }
    }
    out.close();

    // Quick RD estimate at 2023
    std::ifstream in("../output/sim_panel.csv");
    std::string hdr; std::getline(in,hdr);
    double sa=0,sb=0; int na=0,nb=0;
    std::string line;
    while(std::getline(in,line)){
        size_t p=0; double yr=0,run=0,mer=0;
        for(int c=0;c<8;c++){
            auto np=line.find(',',p);
            auto tok=line.substr(p,np-p); p=np+1;
            if(c==1)yr=std::stod(tok);
            if(c==4)run=std::stod(tok);
            if(c==7)mer=std::stod(tok);
        }
        if((int)yr==2023){
            if(run>=0&&run<=0.1){sa+=mer;na++;}
            if(run<0&&run>=-0.1){sb+=mer;nb++;}
        }
    }
    std::ofstream rd("../output/cpp_rd_demo.txt");
    rd<<"RD demo (2023): mean meritocracy above - below (|running|<=0.1)\n"
      <<"n_above="<<na<<" n_below="<<nb<<" diff="<<(sa/std::max(1,na)-sb/std::max(1,nb))<<"\n";
    std::cout<<"[OK] Outputs in ../output/\n";
}

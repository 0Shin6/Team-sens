import React from "react";
import { Card, CardContent } from "../../components/ui/card";

export const APropos = (): JSX.Element => {
  const navigationItems = [
    { label: "Acceuil", width: "w-[70px]" },
    { label: "Rosters", width: "w-[83px]" },
    { label: "Nos réseaux", width: "w-[114px]" },
    { label: "Boutique", width: "w-[84.64px]" },
    { label: "Nos sponsors", width: "w-28" },
    { label: "Loi 1901", width: "w-[68px]" },
    { label: "Nous contacter", width: "w-[135px]" },
  ];

  const textBlocks = [
    {
      top: "top-[295px]",
      content:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec tempus diam at sem elementum interdum. Donec sodales risus ut nunc dictum gravida. Nullam diam nibh, molestie a diam nec, dignissim ornare ante. In hac habitasse platea dictumst. Nulla suscipit condimentum sapien at porta. Nulla at rhoncus enim. Etiam dui erat, tempor consectetur ipsum sit amet, egestas interdum turpis. Morbi ornare nisi sit amet molestie rutrum. Nullam arcu tellus, eleifend ut erat ut, rutrum volutpat augue. Donec feugiat velit urna, at condimentum ante mollis a. Quisque scelerisque, leo convallis convallis sodales, sem nibh dictum erat, eu congue dolor lectus sed arcu. Nulla velit nisi, hendrerit id viverra ac, aliquam id leo. Sed et aliquam arcu. Mauris pretium velit erat, in malesuada nulla molestie id.",
    },
    {
      top: "top-[588px]",
      content:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec tempus diam at sem elementum interdum. Donec sodales risus ut nunc dictum gravida. Nullam diam nibh, molestie a diam nec, dignissim ornare ante. In hac habitasse platea dictumst. Nulla suscipit condimentum sapien at porta. Nulla at rhoncus enim. Etiam dui erat, tempor consectetur ipsum sit amet, egestas interdum turpis. Morbi ornare nisi sit amet molestie rutrum. Nullam arcu tellus, eleifend ut erat ut, rutrum volutpat augue. Donec feugiat velit urna, at condimentum ante mollis a. Quisque scelerisque, leo convallis convallis sodales, sem nibh dictum erat, eu congue dolor lectus sed arcu. Nulla velit nisi, hendrerit id viverra ac, aliquam id leo. Sed et aliquam arcu. Mauris pretium velit erat, in malesuada nulla molestie id.",
    },
  ];

  const placeholderBoxes = [{ top: "top-80" }, { top: "top-[617px]" }];

  return (
    <main className="bg-transparent grid justify-items-center [align-items:start] w-screen">
      <div className="[background:url(..//a-propos.png)_50%_50%_/_cover] w-[1440px] h-[1080px] relative">
        {placeholderBoxes.map((box, index) => (
          <Card
            key={`placeholder-${index}`}
            className={`absolute w-[200px] h-[200px] ${box.top} left-[1067px] bg-[#d9d9d9] rounded-[40px] border-0`}
          >
            <CardContent className="p-0 w-full h-full" />
          </Card>
        ))}

        {textBlocks.map((block, index) => (
          <div
            key={`text-block-${index}`}
            className={`absolute w-[859px] h-[255px] ${block.top} left-[113px] [font-family:'Plus_Jakarta_Sans',Helvetica] font-medium text-white text-base tracking-[0.32px] leading-[normal]`}
          >
            {block.content}
          </div>
        ))}

        <h1 className="absolute w-[637px] h-20 top-[157px] left-56 [text-shadow:0px_4px_30px_#fff7f7cc] [font-family:'Plus_Jakarta_Sans',Helvetica] font-extrabold text-white text-[64px] text-center tracking-[1.28px] leading-[normal]">
          Qui sommes nous ?
        </h1>

        <footer className="absolute w-[1440px] h-[85px] top-[995px] left-0 bg-[#22222259] backdrop-blur-[7.5px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(7.5px)_brightness(100%)]">
          <div className="absolute w-[514px] h-9 top-6 left-[463px] [font-family:'Plus_Jakarta_Sans',Helvetica] font-bold text-[#fffefe] text-[22px] text-center tracking-[0.44px] leading-[normal]">
            Copyright - Team Sens, Tous droits réservés
          </div>
        </footer>

        <div className="absolute w-[1440px] h-[100px] top-0 left-0">
          <div className="h-[100px]">
            <div className="relative w-[1440px] h-[100px]">
              <header className="inline-flex items-center absolute top-0 left-0 bg-transparent">
                <div className="relative w-[100px] h-[100px] bg-[#0000004c] backdrop-blur-[7.5px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(7.5px)_brightness(100%)] bg-[url(/logo-seul-1.png)] bg-cover bg-[50%_50%]" />

                <div className="relative w-[1340px] h-[100px] bg-[#00000059] shadow-[0px_4.36px_16px_-2.18px_#0000001a] backdrop-blur-[7.5px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(7.5px)_brightness(100%)]" />
              </header>

              <nav className="inline-flex items-start gap-[30px] absolute top-10 left-[531px]">
                {navigationItems.map((item, index) => (
                  <div
                    key={`nav-${index}`}
                    className={`${item.width} h-5 relative mt-[-1.00px] [font-family:'Plus_Jakarta_Sans',Helvetica] font-semibold text-white text-[15px] text-center tracking-[0.30px] leading-[normal] cursor-pointer hover:opacity-80 transition-opacity`}
                  >
                    {item.label}
                  </div>
                ))}
              </nav>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};

package com.example.demo;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

// このクラスが「Webページを返す」役割であることを示す
@Controller
public class PageController {

    // "/greeting" というURLへのアクセスを処理するメソッド
    @GetMapping("/greeting")
    public String showGreetingPage(Model model) {
        // HTMLに渡すデータを設定する
        // "message" という名前で "コントローラーから来ました！" という文字列を渡す
        model.addAttribute("message", "コントローラーから来ました！");

        // "greeting" という名前のHTMLファイルを表示するようSpringに依頼する
        return "greeting";
    }
}